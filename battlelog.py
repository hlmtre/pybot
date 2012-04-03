import urllib2
import json
import bf3api


usernameDict = {}

#fact options: accuracy, skillchange, kills, kd
def getLatestGameFact(api, name, fact):
	gameData = getLatestGameData(api, name)
	if fact in gameData:
		return gameData[fact]
	else:
		return "not available"

def getLatestGameData(api, name):
	username = getusername(api, name)
	latestGameToken = getRecentGameTokens(username)[0]
	gameData = getGameData(latestGameToken)
	return gameData

def getGameData(gameToken):
	baseurl = "http://battlelog.battlefield.com/bf3/battlereport/loadplayerreport"
	url = baseurl + "/" + gameToken[0] + "/2/" + gameToken[1]

	con = urllib2.urlopen(url)
	result = con.read()
	con.close()
	raw = json.loads(result)
	idat = raw["playerReport"]["intData"]
	fdat = raw["playerReport"]["floatData"]
	data = {}
	#if you got no kills, the data will be completely missing, so be careful here.
	if "c___shw_g" in idat and "c___sfw_g" in idat:
		data["accuracy"] = float(idat["c___shw_g"]) / float(idat["c___sfw_g"])
	if "elo" in fdat:
		data["skillchange"] = float(fdat["elo"])
	if "c___k_g" in idat:
		data["kills"] = int(idat["c___k_g"])
		if "c___d_g" in idat:
			data["kd"] = float(idat["c___k_g"]) / float(idat["c___d_g"])
		else:
			data["kd"] = float(idat["c___k_g"])
	
	return data


def getRecentGameTokens(username):

	url = "http://battlelog.battlefield.com/bf3/user/" + username
	
	headers = {'X-AjaxNavigation': 1}
	req = urllib2.Request(url, None, headers)
	con = urllib2.urlopen(req)
	result = con.read()
	con.close()
	raw_data = json.loads(result)
	
	group = raw_data["context"]["gameReportPreviewGroups"]
	#The data coming from battlelog is weird. There's a list of lists, and the
	#placement and length of inner lists is seemingly unpredictable.
	flatlist = []
	for outerindex in range(0, len(group)):
		for innerindex in range(0, len(group[outerindex])):
			flatlist.append(group[outerindex][innerindex])
	
	data = []
	for i in range(0, len(flatlist)):
		token = (flatlist[i]["reportId"], flatlist[i]["personaId"])
		data.append(token)
	
	return data

	
def getusername(api, name):
	global usernameDict
	if name in usernameDict:
		return usernameDict[name]
	
	data = api.player(name, None, "clear,urls")
	statsurl = data.battlelog
	headers = {'X-AjaxNavigation': 1}
	req = urllib2.Request(statsurl, None, headers)
	con = urllib2.urlopen(req)
	result = con.read()
	con.close()
	raw_data = json.loads(result)
	username = raw_data["context"]["profileCommon"]["user"]["username"]
	usernameDict[name] = username
	return username
	
