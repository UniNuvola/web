package routes

import (
	"github.com/gofiber/fiber/v2"
)

func info(c *fiber.Ctx) error {
	return c.Render("info", fiber.Map{})
}

func docs(c *fiber.Ctx) error {
	return c.Render("docs", fiber.Map{})
}
