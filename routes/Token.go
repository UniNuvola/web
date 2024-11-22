package routes

import (
	"encoding/json"

	"github.com/gofiber/fiber/v2/log"
)

type Token struct {
	Iss      string            `json:"iss"`
	UserID   string            `json:"UserID"`
	Provider string            `json:"Provider"`
	Metadata map[string]string `json:"Metadata"`
}

func (t Token) FromJSON(v string) Token {
	err := json.Unmarshal([]byte(v), &t)
	if err != nil {
		log.Fatalf("CANNOT UNMARSHAL USERDATA. ERROR: ", err)
	}

	return t
}
