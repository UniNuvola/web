package db

import (
	"context"
	"errors"
	"strings"
	"time"

	"github.com/gofiber/fiber/v2/log"
	"github.com/redis/go-redis/v9"
)

// Opens connection with Redis db
func open() (*redis.Client, context.Context) {
	connString :=
		"redis://" + configs["USER"] + ":" + configs["PASSWORD"] + "@" + configs["IP"] + ":" + configs["PORT"] + "/" + configs["DB"]
	log.Debugf("CONNECTING TO REDIS: %s", connString)

	opt, err := redis.ParseURL(connString)
	if err != nil {
		log.Fatalf("  FAIL. %s", err)
	}

	rdb := redis.NewClient(opt)
	log.Debug("  OK !")

	return rdb, context.Background()
}

// Get a Redis Key Value.
// Redis Key is in the form of
//
//	prefix:username:key
func get(key string) string {
	log.Debugf("GET KEY: %s", key)

	conn, ctx := open()
	defer conn.Close()

	val, err := conn.Do(ctx, "GET", key).Text()

	switch {
	case err == redis.Nil:
		log.Warnf("Missing key: %s", key)
		val = ""
	case err != nil:
		log.Errorf("Error while getting key %s: %s", key, err)
		val = ""
	case val == "":
		log.Warnf("Empty key %s", key)
		val = ""
	}

	log.Debugf("  VAL: %s", val)

	return val
}

// Set a Redis Key to Value.
// Redis Key is in the form of
//
//	prefix:username:key
func set(key string, value interface{}) {
	log.Debugf("SET KEY: %s --> %s", key, value)

	conn, ctx := open()
	defer conn.Close()

	_, err := conn.Do(ctx, "SET", key, value).Result()
	if err != nil {
		log.Errorf("FAIL SET KEY %s", key)
	}
}

// Get Set Values identified by KEY
//
// This is the result of redis command SMEMBERS
func sGet(key string) []string {
	log.Debugf("SGET KEY: %s", key)

	conn, ctx := open()
	defer conn.Close()

	val, err := conn.SMembers(ctx, key).Result()

	switch {
	case err == redis.Nil:
		log.Warnf("Missing key: %s", key)
		val = []string{}
	case err != nil:
		log.Errorf("Error while getting key %s: %s", key, err)
		val = []string{}
	case len(val) == 0:
		log.Warnf("Empty Set %s", key)
		val = []string{}
	}

	log.Debugf("  VAL: %s", val)
	return val
}

// Append a VALUE to a SET identified by KEY
//
// This is function calls the SADD redis method.
func sAdd(key string, value interface{}) {
	log.Debugf("ADD KEY TO: %s --> %s", key, value)

	conn, ctx := open()
	defer conn.Close()

	err := conn.SAdd(ctx, key, value).Err()

	if err != nil {
		log.Errorf("FAIL ADD KEY %s", key)
	}
}

// Delete a Redis Key.
// Redis Key is in the form of
//
//	prefix:username:key
func del(key string) {
	log.Infof("DELETING KEY %s", key)

	conn, ctx := open()
	defer conn.Close()

	err := conn.Del(ctx, key).Err()
	if err != nil {
		log.Errorf("CANNOT DELETE KEY: %s", key)
	}
}

// Add a new User Request
//
// A User request consists in the following keys:
//   - STARTDATE: request's date
//   - STATUS: request' status. Could be "pending" or "approved"
func AddRequest(user string) error {
	log.Infof("ADDING REQUEST: %s", user)

	if !isValidUser(user) {
		log.Errorf("INVALID USERNAME: %s", user)
		return errors.New("INVALID USERNAME " + user)
	}

	if requestExists(user) {
		log.Error("REQUEST ALREDY EXISTS !")
		return errors.New("REQUEST ALREDY EXISTS !")
	}

	set(getKey(prefix, user, reqKey["startdate"]), time.Now().Format("2006-01-02 15:4:5"))
	set(getKey(prefix, user, reqKey["status"]), requStatus["pending"])

	notifyLDAPSync()

	return nil
}

// Delete a User Reqest.
//
// Deleting a User request means to remove all user's key, so
// all keys matching:
//
//	prefix:username:*
func DelRequest(user string) error {
	log.Infof("DELETING REQUEST: %s", user)

	if !isValidUser(user) {
		log.Errorf("INVALID USERNAME: %s", user)
		return errors.New("INVALID USERNAME " + user)
	}

	if !requestExists(user) {
		log.Errorf("%s REQUEST DO NOT EXISTS !", user)
		return errors.New(user + " REQUEST DO NOT EXISTS !")
	}

	userKesy := getAllUserKeys(prefix, user)
	for _, toRemoveKey := range userKesy {
		del(toRemoveKey)
	}

	return nil
}

// Update a User Request' Status.
//
// When updating a request' status the following action occurs:
//
//  1. Check if username is valid and Request exists
//  2. Generating new request status (pending --> approved, approved --> pending)
//  3. Updating status
//  4. If new status is "approved", then "enddate" is set and "users" are added to groups
//     Else (means from approved to pending) enddate is removed
func UpdateRequestStatus(user string) error {
	log.Infof("UPDATING REQUEST: %s", user)

	if !isValidUser(user) {
		log.Errorf("INVALID USERNAME: %s", user)
		return errors.New("INVALID USERNAME " + user)
	}

	if !requestExists(user) {
		log.Errorf("%s REQUEST DO NOT EXISTS !", user)
		return errors.New(user + " REQUEST DO NOT EXISTS !")
	}

	key := getKey(prefix, user, reqKey["status"])
	actualRequestStatus := get(key)
	log.Debugf("  ACTUAL REQUEST STATUS: %s", actualRequestStatus)

	if actualRequestStatus == "" {
		log.Errorf("EMPTY REQUEST STATUS !")
		return errors.New("EMPTY REQUEST STATUS, CANNOT UPDATE STATUS !")
	}

	newRequestStatus := changeRequestStatus(actualRequestStatus)
	log.Debugf("  NEW REQUEST STATUS: %s", newRequestStatus)

	set(key, newRequestStatus)

	if newRequestStatus == requStatus["approved"] {
		set(getKey(prefix, user, reqKey["enddate"]), time.Now().Format("2006-01-02 15:4:5"))
		sAdd(getKey(prefix, user, reqKey["groups"]), "users")
		notifyLDAPSync()

	} else {
		del(getKey(prefix, user, reqKey["enddate"]))

	}

	return nil
}

// Get all Request data.
//
// Returns a map in the following form:
//
//	map[redisKey] = value
//
// For Example:
//
//	map["status"] = "pending"
//
// Remember, this funcion returns always a map (could be empty) !
func GetRequestData(user string) UserRequest {
	log.Infof("GETTING REQUEST DATA: %s", user)

	if !isValidUser(user) {
		log.Errorf("INVALID USERNAME: %s", user)
		return UserRequest{}.NewEmpty(user)
	}

	if !requestExists(user) {
		log.Errorf("%s REQUEST DO NOT EXISTS !", user)
		return UserRequest{}.NewEmpty(user)
	}

	// First generate a Map
	requestData := make(map[string]interface{}, 0)
	allUserKeys := getAllUserKeys(prefix, user)

	for _, key := range allUserKeys {
		mapKey := key[strings.LastIndex(key, ":")+1:] // last elem after : sep

		switch mapKey {
		case reqKey["groups"]:
			requestData[mapKey] = sGet(getKey(prefix, user, reqKey["groups"]))

		case reqKey["infos"]:
			requestData[mapKey] = getUserInfos(user)

		default:
			requestData[mapKey] = get(key)
		}
	}

	// app other info to user request
	requestData["user"] = user

	result := UserRequest{}.FromMap(requestData)
	log.Debugf("  REQUEST DATA: %+v", result)

	return result
}

func GetAllRequestData() []UserRequest {
	log.Info("GETTING ALL REQUESTS DATA")

	users := getAllUsers(prefix)
	allRequestData := make([]UserRequest, 0)

	for _, user := range users {
		requestData := GetRequestData(user)
		allRequestData = append(allRequestData, requestData)
	}

	log.Debugf("ALL REQUEST DATA: %+v", allRequestData)
	return allRequestData
}
