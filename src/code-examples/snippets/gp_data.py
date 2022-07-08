from gammapy.data import DataStore

data_store = DataStore.from_dir(
    "$GAMMAPY_DATA/hess-dl3-dr1"
)

obs_ids = [23523, 23526, 23559, 23592]

observations = data_store.get_observations(obs_ids)

for obs in observations:
    print(f"Observation id: {obs.obs_id}")
    print(f"Number of events: {len(obs.events)}")
    print(f"Max. area: {obs.aeff.quantity.max()}")
