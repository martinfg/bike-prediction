import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.model_selection import train_test_split

class Dataset():
    def __init__(self, columns, data):
        self._data = self.build_dataframe(columns, data)
        
    def build_dataframe(self, columns, data):
        """
        transform raw row wise data from database to pandas DataFrame
        """
        df = pd.DataFrame(data)
        df.columns = columns
        return df

    def prepare_samples(self, num_history, num_predictions):
        """
        Creates a feature vector by mapping historic and feature values for bree bikes to every row if available,
        otherwise inserts NaN.

        num_history = how many time steps (hours) in the past should be converted to a column
        num_predictions = how many time steps (hours) in the future should be converted to a column
        """
        
        def get_t_values(t_offset, time, location):
            offset_time = time + timedelta(hours=t_offset)
            offset_row = self._data.loc[(self._data['time'] == offset_time) & (self._data['location'] == location)]
            bikes = offset_row['free_bikes'].values
            # return int(bikes[0]) if len(bikes) > 0 else pd.NA # use NA instead of np.nan because nan forces to column to be floats
            return float(bikes[0]) if len(bikes) > 0 else np.nan 

        # mark newly created columns with suffix feature, target for easy distinction between feature and target afterwards
        for t in range(-num_history, num_predictions+1):
            suffix = "feature" if t <= 0 else "target"
            self._data[f'bikes_t{t}_{suffix}'] = self._data.apply(lambda x: get_t_values(t, x['time'], x['location']), axis=1)

        # add total amount of free bikes as feature
        # TODO

        # drop free_bike column
        self._data = self._data.drop(columns=["free_bikes"])


    def get_train_test_split(self, location, test_size=0.2):
        """
        Splits data into train and test split by removing rows with missing values first
        
        test_split = percentage of samples used for test set
        """
        location_specific_data = self._data.loc[self._data["location"] == location]
        data_clean = location_specific_data.dropna()
        feature_cols = [col for col in data_clean.columns if col.endswith("_feature")]
        target_cols = [col for col in data_clean.columns if col.endswith("_target")]
        train, test = train_test_split(data_clean, test_size=test_size, shuffle=True, random_state=42)
        X_train = train[feature_cols]
        y_train = train[target_cols]
        X_test = test[feature_cols]
        y_test = test[target_cols]
        return X_train, y_train, X_test, y_test


    def __getitem__(self, location):
        return self._data.loc[self._data['location'] == location]
