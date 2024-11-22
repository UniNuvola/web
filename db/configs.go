package db

import . "webgo/config"

var configs = map[string]string{
	"IP":       Config("REDIS_IP"),
	"PORT":     Config("REDIS_PORT"),
	"USER":     Config("REDIS_USER"),
	"PASSWORD": Config("REDIS_PASSWORD"),
	"DB":       Config("REDIS_DB"),
}

const prefix = "req"
const infoPrefix = "info"

var requStatus map[string]string = map[string]string{
	"approved": "approved",
	"synced":   "synced",
	"pending":  "pending",
}
var reqKey map[string]string = map[string]string{
	"startdate": "startdate",
	"enddate":   "enddate",
	"status":    "status",
	"groups":    "groups",
}
