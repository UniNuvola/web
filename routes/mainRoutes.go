package routes

import (
	"encoding/json"
	"slices"
	"webgo/db"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/log"
	"github.com/shareed2k/goth_fiber"
)

func home(c *fiber.Ctx) error {
	log.Infof("/ METHOD: %s", c.Method())

	var userData Token

	userString, err := goth_fiber.GetFromSession("user", c)

	// UNLOGGED User
	if err != nil {
		return c.Render("users/unlogged", fiber.Map{})
	}

	// LOGGED User
	log.Info("User LOGGED !")
	log.Debug(userString)

	// unmarshalling
	userData = Token{}.FromJSON(userString)
	log.Debugf("USERDATA: %+v", userData)

	// WARNING: ONLY FOR TESTS !
	userRequestData := db.GetRequestData("nv9800011")
	log.Debugf("USER REQUEST DATA: %+v", userRequestData)
	// userRequestData := db.GetRequestData(userData.Metadata["name"])

	// ADMIN USER
	if slices.Contains(userRequestData.Groups, "admin") {
		log.Debugf("USER %s IS ADMIN", userRequestData.User)

		allRequests := db.GetAllRequestData()
		log.Debugf("ALL REQUESTS: %s", allRequests)

		return c.Render("users/admin", fiber.Map{
			"user":         userRequestData,
			"uninuvolaurl": "https://google.it",
			"allRequests":  allRequests,
		})

	}

	// NORMAL USER
	log.Debugf("USER %s IS NORMAL USER", userRequestData.User)

	switch c.Method() {
	case "POST":
		db.AddRequest(userRequestData.User)
	default:
		log.Debug("nothing to do")
	}

	return c.Render("users/user", fiber.Map{
		"user":         userRequestData,
		"uninuvolaurl": "https://google.it"})

}

func auth(c *fiber.Ctx) error {
	user, err := goth_fiber.CompleteUserAuth(c)
	if err != nil {
		log.Fatal(err)
	}

	log.Info("SUCCESSFULLY LOGGED USER")
	log.Debug(user)

	jsonUser, err := json.Marshal(user)
	if err != nil {
		log.Fatal("CANNOT MARSHALL MAP TO JSON %s", user)
	}

	goth_fiber.StoreInSession("user", string(jsonUser), c)

	return c.Redirect("/")
}

// Redirect to correct path
func login(c *fiber.Ctx) error {
	log.Infof("/login METHOD: %s", c.Method())

	return c.Redirect("/login/openid-connect")
}
