package config

import (
	"os"

	"github.com/gofiber/fiber/v2/log"
	"github.com/joho/godotenv"
)

// Config func to get env value
func Config(key string) string {
	err := godotenv.Load(".env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	value := os.Getenv(key)
	log.Debugf(".ENV KEY %s: %s", key, value)

	return value
}
