package db

import (
	"maps"
	"slices"
	"strings"

	// "structs"

	"github.com/gofiber/fiber/v2/log"
)

func getKey(values ...string) string {
	return strings.Join(values, ":")
}

func isValidUser(user string) bool {
	if user != "" {
		return true
	}

	return false
}

func getAllUsers(perifx string) []string {
	log.Debug("Getting All User")

	conn, ctx := open()
	defer conn.Close()

	request := prefix + ":*"
	log.Debugf("  SCAN %s", request)

	// map keys are a Set !!
	// using this var to ave a Set of users
	foundUsers := make(map[string]interface{}, 0)

	iter := conn.Scan(ctx, 0, request, 0).Iterator()
	for iter.Next(ctx) {
		val := iter.Val()
		user := strings.Split(val, ":")[1]

		foundUsers[user] = nil
	}

	if err := iter.Err(); err != nil {
		log.Errorf("  ERROR: %s", err)
	}

	users := slices.Collect(maps.Keys(foundUsers))
	log.Debugf("  FOUND USERS: %s", users)

	return users

}

func getAllUserKeys(prefix string, user string) []string {
	log.Debugf("Getting All User %s Keys", user)

	if !isValidUser(user) {
		log.Errorf("NOT A VALID USER %s", user)
		return []string{}
	}

	conn, ctx := open()
	defer conn.Close()

	request := prefix + ":" + user + ":*"
	log.Debugf("  SCAN %s", request)

	foundKeys := make([]string, 0)
	iter := conn.Scan(ctx, 0, request, 0).Iterator()
	for iter.Next(ctx) {
		val := iter.Val()
		foundKeys = append(foundKeys, val)
	}

	if err := iter.Err(); err != nil {
		log.Errorf("  ERROR: %s", err)
	}

	log.Debugf("  FOUND KEYS: %s", foundKeys)

	return foundKeys
}

func requestExists(user string) bool {
	log.Infof("CHECKING %s REQUEST EXISTENCE", user)

	if !isValidUser(user) {
		log.Errorf("  NOT A VALID USERNAME %s", user)
		return true // force to stop calling function
	}

	conn, ctx := open()
	defer conn.Close()

	request := prefix + ":" + user + ":*"
	log.Debugf("  SCAN %s", request)

	keysFound := 0

	iter := conn.Scan(ctx, 0, request, 0).Iterator()
	for iter.Next(ctx) {
		log.Debugf("    %s", iter.Val())
		keysFound++
	}
	if err := iter.Err(); err != nil {
		log.Errorf("  ERROR: %s", err)
	}

	if keysFound > 0 {
		return true
	}

	return false
}

func changeRequestStatus(status string) string {
	switch status {
	case requStatus["pending"]:
		return requStatus["approved"]

	case requStatus["approved"]:
		return requStatus["pending"]
	}

	// WARNING: code execution should never reach
	// 					this point !!
	return status
}

func getUserInfos(user string) map[string]string {
	log.Debugf("GETTING USER INFO: %s", user)

	if !isValidUser(user) {
		log.Errorf("INVALID USERNAME: %s", user)
		return map[string]string{}
	}

	if !requestExists(user) {
		log.Errorf("%s REQUEST DO NOT EXISTS !", user)
		return map[string]string{}
	}

	userInfos := make(map[string]string, 0)
	userInfoKeys := getAllUserKeys(infoPrefix, user)
	log.Debugf("USER INFOS KEYS: %s", userInfoKeys)

	for _, key := range userInfoKeys {
		mapKey := key[strings.LastIndex(key, ":")+1:] // last elem after : sep
		userInfos[mapKey] = get(key)
	}

	log.Debugf("USER INFOS: %#v", userInfos)
	return userInfos
}

func notifyLDAPSync() {
	//TODO:
}
