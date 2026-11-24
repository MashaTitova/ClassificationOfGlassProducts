import os
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
from typing import Optional

FEATURE_COLUMNS = ['RI', 'Na', 'Mg', 'Al', 'Si', 'K', 'Ca', 'Ba', 'Fe']
TARGET_COLUMN = 'Type'
DEFAULT_DATA_FILE = 'glassData.txt'

@dataclass
class Dataset:
    raw: pd.DataFrame
    X: pd.DataFrame
    y: pd.Series
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    source_path: str

class DataModel:
    def __init__(self):
        self._dataset: Optional[Dataset] = None

    @property
    def dataset(self) -> Optional[Dataset]:
        return self._dataset

    @property
    def project_root(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def default_data_path(self) -> str:
        return os.path.join(self.project_root, DEFAULT_DATA_FILE)

    def load(self, path: str) -> Dataset:
        df = pd.read_csv(path, sep=",")
        if "Id" in df.columns:
            df = df.drop(columns=["Id"])
        X = df.drop(TARGET_COLUMN, axis=1)
        y = df[TARGET_COLUMN]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        self._dataset = Dataset(
            raw=df, X=X, y=y,
            X_train=X_train, X_test=X_test,
            y_train=y_train, y_test=y_test,
            source_path=path
        )
        return self._dataset

    def load_default(self) -> Dataset:
        path = self.default_data_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл данных не найден: {path}")
        return self.load(path)

    REQUIRED_FEATURES = set(FEATURE_COLUMNS)

    def load_from_bytes(self, content: bytes, source: str) -> bool:
        """Универсальная загрузка: названия и количество колонок берутся из первой строки файла."""
        from sklearn.model_selection import train_test_split

        try:
            text = content.decode("utf-8-sig", errors="replace")
        except Exception as e:
            print(f"Не удалось декодировать файл: {e}")
            return False

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if len(lines) < 3:
            print("Слишком мало строк в файле")
            return False

        header_line = lines[0]

        candidates = {}
        for sep in [";", "\t", ","]:
            cols = [c.strip() for c in header_line.split(sep)]
            if len(cols) >= 2:
                candidates[sep] = cols
        if not candidates:
            print("Не удалось разбить заголовок")
            return False
        sep, columns = max(candidates.items(), key=lambda kv: len(kv[1]))
        columns = [c for c in columns if c]
        if len(columns) < 2:
            print("В заголовке меньше двух колонок")
            return False
        print(f"Заголовок: {columns} (разделитель {sep})")

        # строки данных
        rows = []
        skipped = 0
        for ln in lines[1:]:
            parts = [p.strip() for p in ln.split(sep)]
            if len(parts) != len(columns):
                skipped += 1
                continue
            rows.append(parts)
        print(f"Строк принято: {len(rows)}, пропущено (число полей не совпало): {skipped}")
        if len(rows) < 2:
            print("Слишком мало корректных строк данных")
            return False

        df = pd.DataFrame(rows, columns=columns)

        # целевая колонка: по имени, иначе последняя
        target_aliases = {"type", "target", "class", "label", "y",
                          "класс", "тип", "цель"}
        lower_cols = [c.lower() for c in columns]
        target_idx = next((i for i, c in enumerate(lower_cols) if c in target_aliases), None)
        if target_idx is None:
            target_idx = len(columns) - 1
            print(f"Целевая колонка по имени не найдена, берется последняя: {columns[target_idx]}")
        target_name = columns[target_idx]
        feature_cols = [
            c for i, c in enumerate(columns)
            if i != target_idx and c.lower() not in ("id", "index", "№")
        ]

        # числовые признаки и цель
        for c in feature_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df[target_name] = pd.to_numeric(df[target_name], errors="coerce")

        # очистка: и по признакам, и по целевой колонке — NaN в Type больше не пройдут
        before = len(df)
        df = df.dropna(subset=feature_cols + [target_name]).reset_index(drop=True)
        if len(df) < 2:
            print("После очистки не осталось числовых строк")
            return False
        if before - len(df):
            print(f"Выброшено строк с пропусками: {before - len(df)}")

        # теперь NaN в цели нет — каст безопасен
        df[target_name] = df[target_name].astype(int)

        X = df[feature_cols]
        y = df[target_name]

        # разбиение на train/test — с защитой от слишком маленьких выборок
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        except ValueError:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

        self._dataset = Dataset(
            raw=df, X=X, y=y,
            X_train=X_train, X_test=X_test,
            y_train=y_train, y_test=y_test,
            source_path=source
        )
        # динамические списки колонок — их читают predict и OLAP
        self.feature_columns = feature_cols
        self.target = target_name
        print(f"Итог: {len(df)} объектов, признаков {len(feature_cols)}, цель '{target_name}'")
        return True



    def preview(self, n: int = 5) -> str:
        """Первые n строк в виде: [1] RI = 1.52; Na = 13.64; ..."""
        if self._dataset is None:
            return ""
        df = self._dataset.raw.head(n)
        cols = list(df.columns)
        lines = []
        for i, (_, row) in enumerate(df.iterrows(), 1):
            pairs = "; ".join(f"{c}={row[c]}" for c in cols)
            lines.append(f"[{i}] {pairs}")
        return "\n".join(lines)
