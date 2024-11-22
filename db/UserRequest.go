package db

import (
	"encoding/json"

	"github.com/gofiber/fiber/v2/log"
)

type UserRequest struct {
	Startdate string            `json:"startdate"`
	Enddate   string            `json:"enddate"`
	Status    string            `json:"status"`
	Groups    []string          `json:"groups"`
	User      string            `json:"user"`
	Infos     map[string]string `json:"infos"`
	Empty     bool
}

func (c UserRequest) FromMap(v map[string]interface{}) UserRequest {
	mapToJson, err := json.Marshal(v)
	if err != nil {
		log.Fatal("Cannot convert map to json !")
	}

	json.Unmarshal(mapToJson, &c)

	c.Empty = c.IsEmpty()

	return c
}

func (c UserRequest) IsEmpty() bool {
	if c.Startdate == "" || c.Status == "" || c.User == "" {
		return true
	}

	return false
}

func (c UserRequest) NewEmpty(user string) UserRequest {
	return UserRequest{Empty: true, User: user}
}
