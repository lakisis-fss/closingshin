/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_1592764591")

  // update collection data
  unmarshal({
    "indexes": [
      "CREATE INDEX `idx_ohlcv_code_date` ON `ohlcv` (`code`, `date`)"
    ]
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_1592764591")

  // update collection data
  unmarshal({
    "indexes": []
  }, collection)

  return app.save(collection)
})
