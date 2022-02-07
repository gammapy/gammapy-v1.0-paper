from gammapy.makers import MapDatasetMaker, FoVBackgroundMaker, SafeMaskMaker

maker = MapDatasetMaker()
bkg_maker = FoVBackgroundMaker()
mask_maker = SafeMaskMaker()

dataset = maker.run(dataset, observation)
dataset = mask_maker.run(dataset,observation)
dataset = bkg_maker.run(dataset,observation)

