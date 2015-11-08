from urllib2 import urlopen
from urllib import urlencode
from json import load
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
        """
        Creates meetup client object.

        Args:
            key (string) - Meetup API key
            paging (int) - number of results per request (200 by default)
        """
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
        jsonResponse = load(response)
        return jsonResponse['results']

    def findMembersByGroup(self, groupName=None, groupId=None):
        """
        Returns list of meetup group members.
        
        Args:
            groupName (string) - url name of the group (either groupId or groupName needs to be present)
            groupId (string) - unique identifier of the group (either groupId or groupName needs to be present)

        Returns: list of MeetupMember objects.
        """

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
        """
        Returns list of groups subscribed by meetup user.
        
        Args:
            memberId (string) - unique identifier of meetup user.

        Returns: list of MeetupGroup objects.
        """

        response = self._sendRequest('groups',{'member_id':memberId})
        groups = []
        for group in response:
            groups.append(MeetupGroup(group, self))
        return groups

    def findGroupByName(self, groupName=None, groupID=None):
        """
        Returns MeetupGroup object based on group name or ID .
        
        Args:
            groupName (string) - url name of the group (either groupId or groupName needs to be present)
            groupId (string) - unique identifier of the group (either groupId or groupName needs to be present)

        Returns: MeetupGroup object.
        """

        if groupName:
            response = self._sendRequest('groups', {'group_urlname': groupName})
        elif groupID:
            response = self._sendRequest('groups', {'group_id': groupID})
        else:
            raise AttributeError("Either groupName or groupId is required")
        return MeetupGroup(response[0], self)

    def findEventsByGroup(self, groupName=None, groupId=None, eventStatus=EventStatus.All):
        """
        Returns list of events related to group.
        
        Args:
            groupName (string) - url name of the group (either groupId or groupName needs to be present)
            groupId (string) - unique identifier of the group (either groupId or groupName needs to be present)
            eventStatus (list)- states of events to be returned (see EventStatus class for more details). By default, returns all group events.

        Returns: list of MeetupEvent objects.

        Example:
            Find all past and upcoming "LondonOnBoard" group events:
            findEventsByGroup(groupName="LondonOnBoard", [EventStatus.Upcoming, EventStatus.Past])
        """
        status = str(eventStatus)[1:-1].replace("'",'').replace(" ","")
        offset =0
        response_length = self.Page
        events = []

        while response_length == self.Page:
            if groupName:
                response = self._sendRequest('events', {'group_urlname':groupName, 'status':status}, offset=offset)
            elif groupId:
                response = self._sendRequest('events', {'group_id': groupId, 'status': status}, offset=offset)
            else:
                response_length = 0
                raise AttributeError("Either groupName or groupId is required")
            response_length = len(response)
            if response_length == self.Page:
                offset += 1
            for event in response:
                events.append(MeetupEvent(event, self))
        return events

def convertTimestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp/1000)

class MeetupMetaObject(object):   
    def __init__(self, dictionary, client):
        self._json_dictionary = dictionary
        self._mClient = client

    def __getattr__(self, name):
        try:
            return self._json_dictionary[name]
        except:
            raise AttributeError

    def __dir__(self):
        return [str(i) for i in self._json_dictionary.keys()]


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
            return MeetupMetaObject.__getattr__(self, name)

    def __dir__(self):
        #extending REST API with events property
        return [str(i) for i in self._json_dictionary.keys()+['events']]


