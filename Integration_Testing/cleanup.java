package Integration_Testing;

import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.testng.annotations.Test;

public class cleanup {

     @Test
     public void deleteAccount(){
          RestAssured.baseURI = "https://template.postman-echo.com";
          Response response = null;
          response = RestAssured.given().header("api-key","MYkUuzDF.h4dPhkxnKtKoRF08XB8zL").when().pathParam("id",1830875).delete("/api/v1/accounts/:{id}");
          String respbody = response.asPrettyString();
          System.out.println(respbody);
     }
}
