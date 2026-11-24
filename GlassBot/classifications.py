from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV


def decision_tree_classifier(X_train, y_train, X_test, params):
    """
    Обучает дерево решений.
    Если params=None — делает GridSearch по сетке параметров.
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("tree", DecisionTreeClassifier(
            random_state=42,
            max_depth=params.get('max_depth'),
            min_samples_split=params.get('min_samples_split', 2),
            min_samples_leaf=params.get('min_samples_leaf', 1)
        ))
    ])
    pipeline.fit(X_train, y_train)
    best_model = pipeline

    y_pred = best_model.predict(X_test)
    return y_pred, best_model


def k_neighbors_classifier(X_train, y_train, X_test, params):
    """
    Обучает KNN.
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(
            n_neighbors=params.get('n_neighbors', 5),
            weights=params.get('weights', 'uniform'),
            metric=params.get('metric', 'euclidean')
        ))
    ])
    pipeline.fit(X_train, y_train)
    best_model = pipeline

    y_pred = best_model.predict(X_test)
    return y_pred, best_model


def logistic_regression_classifier(X_train, y_train, X_test, params):
    """
    Обучает логистическую регрессию.
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            C=params.get('C', 1.0),
            solver=params.get('solver', 'lbfgs'),
            max_iter=params.get('max_iter', 3000),
            class_weight=params.get('class_weight'),
            random_state=42
        ))
    ])
    pipeline.fit(X_train, y_train)
    best_model = pipeline

    y_pred = best_model.predict(X_test)
    return y_pred, best_model