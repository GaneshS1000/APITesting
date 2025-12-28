package Integration_Testing;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.json.simple.JSONObject;
import org.testng.annotations.Test;

import java.util.HashMap;
import java.util.Map;
import static io.restassured.module.jsv.JsonSchemaValidator.matchesJsonSchemaInClasspath;
public class checkIfCosmicCoinsCanBeDeposited extends CosmicDataForTest{

    @Test(dataProvider = "DataForTest")
    public void createAccount(String owner,int balance,String currency){
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
        String responseBody = response.body().asString();
        System.out.println(responseBody);
        String accountId = response.path("account.id").toString();
        System.out.println("Account ID:"+accountId);
    }

    @Test
    public void checkIfATMAcceptsCosmicCoins(){
        RestAssured.baseURI = "https://template.postman-echo.com/api/v1";
        Response response = null;
        response = RestAssured.given().header("api-key","12345").when().get("/locations").then().extract().response();
        System.out.println(response.asPrettyString());
    }

    @Test
    public void atmAcceptanceSchemaValidation(){
        RestAssured.baseURI = "https://template.postman-echo.com/api/v1";
        Response response = null;
        RestAssured.given().header("api-key","12345").when().get("/locations").then().assertThat()
                .body(matchesJsonSchemaInClasspath("atmAcceptanceSchema.json"));
    }
    @Test(dataProvider = "TransactionDataForPost")
    public void createTransaction(int fromAccountId,int toAccountId,int amount,String currency){
        Map<String,Object> map = new HashMap<>();
        map.put("fromAccountId",fromAccountId);
        map.put("toAccountId",toAccountId);
        map.put("amount",amount);
        map.put("currency",currency);
        System.out.println(map);
        JSONObject request = new JSONObject(map);
        Response response = RestAssured.given().header("api-key","PFA0uLFw.Mw8JhFiDrfK6EvJh1Q29Z")
                .contentType(ContentType.JSON)
                .accept(ContentType.JSON)
                .body(request.toJSONString())
                .when()
                .post("https://template.postman-echo.com/api/v1/transactions");
        response.then().log();
        assert response.statusCode() == 200;
        String responseBody = response.body().asString();
        System.out.println(responseBody);
        String transactionId = response.path("transaction.id").toString();
        System.out.println("Transaction ID:"+transactionId);
    }


}
