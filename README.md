# meetuplib
Simple Python Meetup API wrapper

## Short description
Metuplib is Python library aiming to implement [Meetup.com API v2](http://www.meetup.com/meetup_api/). It does not yet cover all existing features, but should be good enough for most important classes (ie. Groups, Members, Events). It tries to mimic as closely as possible already existing methods and properties with a bit of syntax sugar provided by Python itself.

## Getting started - a few practical examples
Meetuplib currently supports API key authentication only, therefore the first step to make examples below working is to [get your own key](https://secure.meetup.com/meetup_api/key/). Once you have it, you may start exploring the data.

### Creating MeetupClient object
To start working with meetup API it is required to create an instance of MeetupClient class. It is very straightforward - the only required parameter is your API key:

```python
from meetuplib import MeetupClient
mclient = MeetupClient("#MY_SECRET_API_KEY")
```
### Exploring meetup groups
Meetup groups are one of most important entities, gathering information about user groups. Here's how you can find basic group information (all object properties are derived from [official docs](http://www.meetup.com/meetup_api/docs/2/groups/)]:

```python
LOBgroup = mclient.findGroupByName("LondonOnBoard")
LOBgroup.name, LOBgroup.country, LOBgroup.created
(u'London On Board', u'GB', datetime.datetime(2006, 6, 30, 9, 55, 39))
```

### Exploring meetup events
As events are always related to particular group, meetuplib provides two ways of dealing with them - using `findEventsByGroup()` method or `events` property:
```
firstEvent = mclient.findEventsByGroup("LondonOnBoard")[-1].name
lastEvent = LOBgroup.events[0].name
```

### Exploring meetup members
As with events you may easily get information about group members:
```python
firstMember = mclient.findMembersByGroup("LondonOnBoard")[-1].name
```

##Release notes

### 0.25
* Fixed paging in findEventsByGroup() method
* Added proper object discovery (ie. dir(MeetupGroup))
* Added docstrings to MeetupClient public methods