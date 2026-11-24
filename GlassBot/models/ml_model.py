# -*- coding: utf-8 -*-
import os
import joblib
import numpy as np
import pandas as pd
import math
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score,
    f1_score, accuracy_score, roc_curve, auc
)
from sklearn.preprocessing import label_binarize
import classifications


class MLModel:
    MODEL_LR = "Logistic Regression"
    MODEL_KNN = "KNN"
    MODEL_DT = "Decision Tree"

    def __init__(self):
        self._model = None
        self._y_pred = None
        self._model_type = None
        self._last_X_test = None
        self._feature_names = None

    @property
    def model(self): return self._model
    @property
    def y_pred(self): return self._y_pred
    @property
    def is_trained(self) -> bool: return self._model is not None

    def set_last_X_test(self, X_test): self._last_X_test = X_test
    def set_feature_names(self, names): self._feature_names = list(names)

    def train(self, model_type: str, X_train, y_train, X_test, params: Dict) -> np.ndarray:
        self._model_type = model_type
        if model_type == self.MODEL_LR:
            y_pred, model = classifications.logistic_regression_classifier(
                X_train, y_train, X_test, params)
        elif model_type == self.MODEL_KNN:
            y_pred, model = classifications.k_neighbors_classifier(
                X_train, y_train, X_test, params)
        elif model_type == self.MODEL_DT:
            y_pred, model = classifications.decision_tree_classifier(
                X_train, y_train, X_test, params)
        else:
            raise ValueError(f"Неизвестная модель: {model_type}")
        self._model = model
        self._y_pred = y_pred
        return y_pred

    def save(self) -> str:
        if not self.is_trained:
            raise RuntimeError("Нет обученной модели")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if hasattr(self._model, 'named_steps'):
            clf = list(self._model.named_steps.values())[-1]
            name = clf.__class__.__name__.lower()
        else:
            name = self._model.__class__.__name__.lower()
        models_dir = os.path.join(self.project_root, 'data', 'models')
        os.makedirs(models_dir, exist_ok=True)
        path = os.path.join(models_dir, f"{name}_{ts}_model.pkl")
        joblib.dump(self._model, path)
        return path

    def load(self, path: str):
        self._model = joblib.load(path)
        self._y_pred = None
        self._model_type = None

    def predict(self, X) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("Модель не загружена")
        self._y_pred = self._model.predict(X)
        return self._y_pred

    def predict_single(self, features: dict) -> Dict[str, Any]:
        if self._model is None:
            raise RuntimeError("Модель не загружена")
        clean = {k: v for k, v in features.items() if k != 'Id'}
        df = pd.DataFrame([clean])
        pred = self._model.predict(df)[0]
        proba = {}
        try:
            if hasattr(self._model, 'predict_proba'):
                p = self._model.predict_proba(df)[0]
                if hasattr(self._model, 'named_steps'):
                    clf = list(self._model.named_steps.values())[-1]
                    classes = clf.classes_
                elif hasattr(self._model, 'classes_'):
                    classes = self._model.classes_
                else:
                    classes = np.arange(len(p))
                for i, c in enumerate(classes):
                    if i < len(p):
                        proba[int(c)] = float(p[i])
        except Exception as e:
            print(f"[WARNING] predict_proba failed: {e}")
            if hasattr(self._model, 'classes_'):
                classes = self._model.classes_
            elif hasattr(self._model, 'named_steps'):
                clf = list(self._model.named_steps.values())[-1]
                classes = clf.classes_
            else:
                classes = [1, 2, 3, 5, 6, 7]
            proba = {int(c): 1.0/len(classes) for c in classes}
        return {'prediction': int(pred), 'probabilities': proba}

    def evaluate_prediction(self, proba: dict) -> Dict[str, Any]:
        import math
        if not proba:
            return {'confidence': 0.0, 'margin': 0.0, 'entropy': 0.0,
                    'normalized_entropy': 0.0, 'top_classes': []}
        probs = list(proba.values())
        classes = list(proba.keys())
        sorted_pairs = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
        confidence = sorted_pairs[0][1]
        margin = sorted_pairs[0][1] - sorted_pairs[1][1] if len(sorted_pairs) >= 2 else confidence
        entropy = sum(-p * math.log2(p) for p in probs if p > 0)
        max_entropy = math.log2(len(probs)) if len(probs) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        top_classes = [{'class': int(c), 'probability': float(p)}
                       for c, p in sorted_pairs[:3]]
        return {
            'confidence': float(confidence),
            'margin': float(margin),
            'entropy': float(entropy),
            'normalized_entropy': float(normalized_entropy),
            'top_classes': top_classes
        }

    def per_class_metrics(self, y_true) -> Dict[str, np.ndarray]:
        if self._y_pred is None:
            raise RuntimeError("Нет предсказаний")
        all_classes = np.unique(np.concatenate([y_true, self._y_pred]))
        return {
            'precision': precision_score(y_true, self._y_pred, average=None,
                                         zero_division=0, labels=all_classes),
            'recall': recall_score(y_true, self._y_pred, average=None,
                                   zero_division=0, labels=all_classes),
            'f1': f1_score(y_true, self._y_pred, average=None,
                           zero_division=0, labels=all_classes),
        }

    def accuracy(self, y_true) -> float:
        if self._y_pred is None:
            raise RuntimeError("Нет предсказаний")
        return accuracy_score(y_true, self._y_pred)

    def confusion_matrix_data(self, y_true) -> np.ndarray:
        if self._y_pred is None:
            raise RuntimeError("Нет предсказаний")
        return confusion_matrix(y_true, self._y_pred)

    def roc_data(self, y_true):
        if not hasattr(self._model, 'predict_proba'):
            raise RuntimeError("Модель не поддерживает predict_proba")
        if self._last_X_test is None:
            raise RuntimeError("X_test не установлен")
        y_score = self._model.predict_proba(self._last_X_test)
        classes = np.unique(y_true)
        y_bin = label_binarize(y_true, classes=classes)
        result = []
        for i, cls in enumerate(classes):
            fpr, tpr, _ = roc_curve(y_bin[:, i], y_score[:, i])
            result.append((cls, fpr, tpr, auc(fpr, tpr)))
        return result

    def get_coefficients(self) -> Optional[Tuple[np.ndarray, list, list]]:
        """Возвращает (coef, feature_names, class_labels)."""
        if not self.is_trained:
            return None
        clf = self._model.named_steps.get('clf') if hasattr(self._model, 'named_steps') else self._model
        if not isinstance(clf, LogisticRegression):
            return None
        return clf.coef_, self._feature_names, list(clf.classes_)


    @property
    def project_root(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))