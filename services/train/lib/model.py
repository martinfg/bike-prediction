import pandas as pd
import mlflow
from sklearn.linear_model import LinearRegression

class PriorValueRegressor:
    """
    Baseline Regressor that assumes amount of free bikes is stable over prediction horizon
    (repeats the current value three times).
    """
    def __init__(self):
        pass

    def train(self, X_train, y_train):
        # the is no actual training with this model
        pass

    def predict(self, X, num_predictions):
        current_values = pd.Series(X["bikes_t0_feature"])
        predictions_df = pd.DataFrame(
            pd.concat([current_values] * num_predictions, axis=1),
        )
        predictions_df.columns = [f"bikes_t{i}_target" for i in range(1, num_predictions+1)]
        return predictions_df

    def test(self, X_test, y_test):
        num_predictions = len(y_test.columns)
        prediction_df = self.predict(X_test, num_predictions)

        # calc MAE (Mean absolute error)
        mae = abs(prediction_df - y_test).sum() / len(prediction_df)
        return {"mae": mae.values}


class LinearRegressor:
    """
    Linear Regressor that uses the last 3 hours for training.
    """
    def __init__(self):
        self._lr_1 = LinearRegression()
        self._lr_2 = LinearRegression()
        self._lr_3 = LinearRegression()

    def train(self, X_train, y_train):
        # initialize 3 regressors, use features to train target 1, target 2 and target 3
        y_train_1 = pd.Series(y_train["bikes_t1_target"])
        y_train_2 = pd.Series(y_train["bikes_t2_target"])
        y_train_3 = pd.Series(y_train["bikes_t3_target"])

        self._lr_1.fit(X_train, y_train_1)
        self._lr_2.fit(X_train, y_train_2)
        self._lr_3.fit(X_train, y_train_3)

    def predict(self, X):
        print("Prediction input:")
        print(X)
        prediction_1_list = self._lr_1.predict(X)
        prediction_2_list = self._lr_2.predict(X)
        prediction_3_list = self._lr_3.predict(X)

        prediction_1_rounded = [round(num) for num in prediction_1_list]
        prediction_2_rounded = [round(num) for num in prediction_2_list]
        prediction_3_rounded = [round(num) for num in prediction_3_list]

        prediction_1_series = pd.Series(prediction_1_rounded)
        prediction_2_series = pd.Series(prediction_2_rounded)
        prediction_3_series = pd.Series(prediction_3_rounded)

        return prediction_1_series, prediction_2_series, prediction_3_series


    def test(self, X_test, y_test):
        # use score from regressor
        prediction_1_series, prediction_2_series, prediction_3_series = self.predict(X=X_test)

        y_test_1 = pd.Series(y_test["bikes_t1_target"])
        y_test_2 = pd.Series(y_test["bikes_t2_target"])
        y_test_3 = pd.Series(y_test["bikes_t3_target"])
        
        # calc MAE (Mean absolute error)
        mae_1_hour = abs(prediction_1_series - y_test_1).sum() / len(prediction_1_series)
        mae_2_hour = abs(prediction_2_series - y_test_2).sum() / len(prediction_2_series)
        mae_3_hour = abs(prediction_3_series - y_test_3).sum() / len(prediction_3_series)
        mae_dict = {"mae": [mae_1_hour, mae_2_hour, mae_3_hour]}

        return mae_dict


class BaselineModel(mlflow.pyfunc.PythonModel):
    def __init__(self, locations, num_predictions):
        self.locations = locations
        self.models = {}
        self.num_predictions = num_predictions

    def train_and_test(self, dataset):
        """
        Trains a separate model for every location within covered area.
        """
        scores = {"overall": {}, "location_specific": {}}
        for location in self.locations:
            # prepare location specific data
            X_train, y_train, X_test, y_test = dataset.get_train_test_split(location=location, test_size=0.2)
            
            # train location specific model
            model = PriorValueRegressor()
            model.train(X_train, y_train)    
            
            # save this model under the location tag
            self.models[location] = model

            # test model performance
            scores['location_specific'][location] = model.test(X_test, y_test)
        
        # calc average error over all locations
        global_mae = None
        for location in self.locations:
            metrics = scores['location_specific'][location]
            if global_mae is None:
                global_mae = metrics['mae']
            else:
                global_mae += metrics['mae']
        global_mae /= len(self.locations)
        scores['overall']['mae'] = global_mae
        return scores

        
    def predict(self, context, model_input):
        predictions = []
        # print(model_input)
        for _, row in model_input.iterrows():
            location = row["location"]
            # select model for given location
            regressor = self.models[location]
            predictions_df = regressor.predict(row, self.num_predictions)
            predictions_values = predictions_df.values[0]
            predictions.append((row["time"], location, *predictions_values))
        return pd.DataFrame(predictions)


class RegressionModel(mlflow.pyfunc.PythonModel):
    def __init__(self, locations):
        self.locations = locations
        self.models = {}

    def train_and_test(self, dataset):
        """
        Trains a separate model for every location within covered area.
        """
        scores = {"overall": {}, "location_specific": {}}
        for location in self.locations:
            # prepare location specific data
            X_train, y_train, X_test, y_test = dataset.get_train_test_split(location=location, test_size=0.2)
            
            # train location specific model
            model = LinearRegressor()
            model.train(X_train, y_train)
            
            # save this model under the location tag
            self.models[location] = model

            # test model performance
            scores['location_specific'][location] = model.test(X_test, y_test)
        
        # # calc average error over all locations and times in the futures
        global_mae_1_hour = None
        global_mae_2_hour = None
        global_mae_3_hour = None

        for location in self.locations:
            metrics = scores['location_specific'][location]

            if global_mae_1_hour is None:
                global_mae_1_hour = metrics['mae'][0]
            else:
                global_mae_1_hour += metrics['mae'][0]

            if global_mae_2_hour is None:
                global_mae_2_hour = metrics['mae'][1]
            else:
                global_mae_2_hour += metrics['mae'][1]

            if global_mae_3_hour is None:
                global_mae_3_hour = metrics['mae'][2]
            else:
                global_mae_3_hour += metrics['mae'][2]
            
        global_mae_1_hour /= len(self.locations)
        global_mae_2_hour /= len(self.locations)
        global_mae_3_hour /= len(self.locations)

        scores['overall']['mae'] = [global_mae_1_hour, global_mae_2_hour, global_mae_3_hour]

        return scores

        
    def predict(self, model_input):
        predictions = []

        for _, row in model_input.iterrows():
            location = row["location"]
            # select model for given location
            regressor = self.models[location]

            # parse row to dataframe to be able to call predict with it
            df = pd.DataFrame([row[['bikes_t-3_feature', 'bikes_t-2_feature', 'bikes_t-1_feature', 'bikes_t0_feature']]])

            prediction_1_series, prediction_2_series, prediction_3_series = regressor.predict(df)

            predictions.append((row["time"], location, prediction_1_series[0], prediction_2_series[0], prediction_3_series[0]))

        return pd.DataFrame(predictions)