package Integration_Testing;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.json.simple.JSONObject;
import org.testng.annotations.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.module.jsv.JsonSchemaValidator.matchesJsonSchemaInClasspath;

public class CheckIfCosmicCoinsAreOpen extends CosmicDataForTest{

    @Test
    public void getAPIKey(){
        RestAssured.baseURI = "https://template.postman-echo.com/api/v1";
        Response response = null;
        response = RestAssured.given().when().get("/auth").then().extract().response();
        String apiKey = response.path("apiKey").toString();
        System.out.println("API Key:"+apiKey);
    }

    @Test(dataProvider = "DataForTest")
    public void createFromAccount(String owner,int balance,String currency){
        Map<String,Object> map = new HashMap<>();
        map.put("owner",owner);
        map.put("balance",balance);
        map.put("currency",currency);
        System.out.println(map);
        JSONObject request = new JSONObject(map);
        Response response = RestAssured.given().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z")
                .contentType(ContentType.JSON)
                .accept(ContentType.JSON)
                .body(request.toJSONString())
                .when()
                .post("https://template.postman-echo.com/api/v1/accounts");
        response.then().log();
        assert response.statusCode() == 200;
        String responseBody = response.body().asString();
        System.out.println(responseBody);
        String accountId = response.path("account.id").toString();
        System.out.println("Account ID:"+accountId);
        Response respAccount =null;
        respAccount = RestAssured.given().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z").when().pathParam("id",accountId).get("https://template.postman-echo.com/api/v1/accounts/{id}").then().extract().response();
        System.out.println(respAccount.asPrettyString());
        RestAssured.given().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z").when().pathParam("id",accountId).get("https://template.postman-echo.com/api/v1/accounts/{id}").then()
                .assertThat().body(matchesJsonSchemaInClasspath("accountSchema.json"));
    }

    /*@Test
    public void getAccountAndSaveCurrency(){
        RestAssured.baseURI = "https://template.postman-echo.com/api/v1";
        Response response = null;
        response = RestAssured.given().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z").when().get("/accounts/1512907").then().extract().response();
        System.out.println(response.asPrettyString());
        assert response.statusCode() == 200;
    }*/

    /*@Test
    public void validate_AccountSchema() throws IOException {
        RestAssured.baseURI = "https://template.postman-echo.com/api/v1";
        Response response = null;
        RestAssured.given().when().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z").get("/accounts/1512547").then().assertThat()
                .body(matchesJsonSchemaInClasspath("accountSchema.json"));
    }*/

    @Test
    public void checkForOpenATMS(){
        RestAssured.baseURI = "https://template.postman-echo.com/api/v1";
        Response response = null;
        response = RestAssured.given().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z").when().get("/locations").then().extract().response();
        System.out.println(response.asPrettyString());
        assert response.statusCode() == 200;
    }

    @Test
    public void ValidateOpenATMSchema(){
        RestAssured.baseURI = "https://template.postman-echo.com/api/v1";
        RestAssured.given().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z").when().get("/locations").then().
        assertThat().body(matchesJsonSchemaInClasspath("openATMSchema.json"));

    }

}
