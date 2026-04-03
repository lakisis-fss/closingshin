/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2816995295")

  // add field
  collection.fields.addAt(17, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text1806468555",
    "max": 0,
    "min": 0,
    "name": "market",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": false,
    "system": false,
    "type": "text"
  }))

  // add field
  collection.fields.addAt(18, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text3485334036",
    "max": 0,
    "min": 0,
    "name": "note",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": false,
    "system": false,
    "type": "text"
  }))

  // add field
  collection.fields.addAt(19, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text2997673066",
    "max": 0,
    "min": 0,
    "name": "vcp_mode",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": false,
    "system": false,
    "type": "text"
  }))

  // add field
  collection.fields.addAt(20, new Field({
    "hidden": false,
    "id": "number318865860",
    "max": null,
    "min": null,
    "name": "close",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(21, new Field({
    "hidden": false,
    "id": "number1677519946",
    "max": null,
    "min": null,
    "name": "last_depth_pct",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(22, new Field({
    "hidden": false,
    "id": "number3891777335",
    "max": null,
    "min": null,
    "name": "vol_ratio",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(23, new Field({
    "hidden": false,
    "id": "number3739198444",
    "max": null,
    "min": null,
    "name": "vcp_score",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  // add field
  collection.fields.addAt(24, new Field({
    "hidden": false,
    "id": "number832464250",
    "max": null,
    "min": null,
    "name": "jump_score",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2816995295")

  // remove field
  collection.fields.removeById("text1806468555")

  // remove field
  collection.fields.removeById("text3485334036")

  // remove field
  collection.fields.removeById("text2997673066")

  // remove field
  collection.fields.removeById("number318865860")

  // remove field
  collection.fields.removeById("number1677519946")

  // remove field
  collection.fields.removeById("number3891777335")

  // remove field
  collection.fields.removeById("number3739198444")

  // remove field
  collection.fields.removeById("number832464250")

  return app.save(collection)
})
