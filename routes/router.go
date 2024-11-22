package routes

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/log"
	"github.com/shareed2k/goth_fiber"
)

var routesToHandlers = map[string]func(c *fiber.Ctx) error{
	"/":                        home,
	"/auth/callback/:provider": auth,
	"/login/:provider":         goth_fiber.BeginAuthHandler,
	"/login":                   login,
	"/info":                    info,
	"/docs":                    docs,
}

func SetRoutes(app *fiber.App) {
	for route, handler := range routesToHandlers {
		log.Infof("ROUTE %s ✅", route)
		log.Debugf("  %s : %s", route, handler)
		app.All(route, handler)
	}
}
