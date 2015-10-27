from urllib2 import urlopen
from urllib import urlencode
import json
from datetime import datetime

PAGE = 200
HTTP_DEBUG = False

class EventStatus:
    Upcoming = "upcoming"
    Past = "past"
    Proposed = "proposed"
    Suggested = "suggested"
    Cancelled = "cancelled"
    Draft = "draft"
    All = ["upcoming", "past", "proposed", "suggested", "cancelled", "draft"]

class MeetupClient:
    def __init__(self, key, paging=PAGE):
        self.URLPrefix = "https://api.meetup.com/2/"
        self.APIKey = key
        self.Page = paging

    def _sendRequest(self, message, params, page=None, offset=None):
        if page is None:
            page = self.Page
        if offset:
            params['offset'] = offset
        params['page'] = page
        params['key'] = self.APIKey
        url = self.URLPrefix+message+"?"+urlencode(params)
        if HTTP_DEBUG:
            print url

        response = urlopen(url)
        jsonResponse = json.load(response)
        return jsonResponse['results']

    def findMembersByGroup(self, groupName=None, groupId=None):
        memberCount = self.findGroupByName(groupName, groupId).members
        if memberCount > self.Page:
            offset = memberCount / self.Page
            if memberCount % self.Page > 0:
                offset += 1
        else:
            offset = 1

        members = []
        for page in range(offset):
            if groupName:
                response = self._sendRequest('members', {'group_urlname':groupName}, offset=page)
            elif groupId:
                response = self._sendRequest('members', {'group_id': groupId}, offset=page)
            else:
                raise AttributeError("Either groupName or groupId is required")
            for member in response:
                members.append(MeetupMember(member, self))
        return members

    def findGroupsByMember(self, memberId):
        response = self._sendRequest('groups',{'member_id':memberId})
        groups = []
        for group in response:
            groups.append(MeetupGroup(group, self))
        return groups

    def findGroupByName(self, groupName=None, groupID=None):
        if groupName:
            response = self._sendRequest('groups', {'group_urlname': groupName})
        elif groupID:
            response = self._sendRequest('groups', {'group_id': groupID})
        else:
            raise AttributeError("Either groupName or groupId is required")
        return MeetupGroup(response[0], self)

    def findEventsByGroup(self, groupName=None, groupId=None, eventStatus=EventStatus.All):
        status = str(eventStatus)[1:-1].replace("'",'').replace(" ","")
        if groupName:
            response = self._sendRequest('events', {'group_urlname':groupName, 'status':status})
        elif groupId:
            response = self._sendRequest('events', {'group_id': groupId, 'status': status})
        else:
            raise AttributeError("Either groupName or groupId is required")
        events = []
        for event in response:
            events.append(MeetupEvent(event, self))
        return events


def convertTimestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp/1000)

class MeetupMetaObject:
    def __init__(self, dictionary, client):
        self._json_dictionary = dictionary
        self._mClient = client

    def __getattr__(self, name):
        return self._json_dictionary.get(name)

class MeetupEvent(MeetupMetaObject):
    def __getattr__(self, name):
        if name == 'time':
            return convertTimestamp(self._json_dictionary['time'])
        else:
            return MeetupMetaObject.__getattr__(self, name)

class MeetupMember(MeetupMetaObject):
    def __getattr__(self, name):
        if name == 'joined':
            return convertTimestamp(self._json_dictionary['joined'])
        else:
            return MeetupMetaObject.__getattr__(self, name)
class MeetupGroup(MeetupMetaObject):
    def __getattr__(self, name):
        if name == 'created':
            return convertTimestamp(self._json_dictionary['created'])
        elif name == 'category':
            return self._json_dictionary['category']['name']
        elif name == 'events':
            return self._mClient.findEventsByGroup(groupId=self._json_dictionary['id'])
        else:
            return self._json_dictionary.get(name)



