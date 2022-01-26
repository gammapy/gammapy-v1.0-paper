from gammapy.data import DataStore

data_store = DataStore.from_dir("$GAMMAPY_DATA")
obs_ids = [1, 2, 3]
observations = data_store.get_observations(obs_ids)
