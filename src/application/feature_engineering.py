import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from typing import Tuple, Any

class FeatureEngineeringPipeline:
    def __init__(self):
        self.numerical_cols = [
            "edad", "puntaje_saber11", "promedio_acumulado", 
            "materias_reprobadas", "ingreso_familiar"
        ]
        self.categorical_cols = [
            "genero", "departamento_origen", "estrato_socioeconomico", 
            "tipo_colegio", "programa_academico"
        ]
        self.target = "desertor"
        self.preprocessor = None

    def prepare_data(self, df: pd.DataFrame) -> Tuple[Any, Any, pd.Series, pd.Series, ColumnTransformer]:
        """Preprocesses dataset and splits it into training and testing structures"""
        X = df[self.numerical_cols + self.categorical_cols]
        y = df[self.target]

        # Define preprocessing for numerical columns
        numerical_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])

        # Define preprocessing for categorical columns
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        # Bundle preprocessing for numerical and categorical data
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, self.numerical_cols),
                ('cat', categorical_transformer, self.categorical_cols)
            ])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Fit preprocessor on training data
        X_train_proc = self.preprocessor.fit_transform(X_train)
        X_test_proc = self.preprocessor.transform(X_test)

        return X_train_proc, X_test_proc, y_train, y_test, self.preprocessor
