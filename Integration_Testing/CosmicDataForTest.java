package Integration_Testing;

import org.testng.annotations.DataProvider;

public class CosmicDataForTest {

    @DataProvider(name = "DataForTest")
    public Object[][] accountDataForPost(){
        return new Object[][]{
                {"RKO",10000,"Dogecoin"},
        };
    }

    @DataProvider(name = "TransactionDataForPost")
    public Object[][] transactionDataForPost(){
        return new Object[][]{
                {1512531,1512440,20,"COSMIC_COINS"},
        };
    }
}
