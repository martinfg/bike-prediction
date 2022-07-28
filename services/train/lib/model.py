import pandas as pd
import numpy as np

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
        current_values = X["bikes_t0_feature"]
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


class BaselineModel:
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

        
    def predict(self, location, sample):
        # select model for given location
        model = self.models[location]
        # make prediction on sample
        return model.predict(sample)
