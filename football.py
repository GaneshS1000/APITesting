#program to test for football API's
import requests

print("List of all Football Leagues:")
headerInfo = {
    "X-Auth-Token" : "476241048d064252a8c68f3e31951a1b",
    "X-Response-Control" : "minified"
}
football_leagues = requests.get("https://api.football-data.org/v4/competitions/2021/teams",headers=headerInfo)
football_leagues_response = football_leagues.json()
print(football_leagues_response)
competitionType = football_leagues_response['competition']['type']
assert competitionType == 'LEAGUE'
#Season Date
print("Season Dates:")
startDate = football_leagues_response['season']['startDate']
endDate = football_leagues_response['season']['endDate']
print("Start Date:",startDate)
print("End Date:",endDate)
#Team Info
teamName = football_leagues_response["teams"][0]
print("Name :",teamName)