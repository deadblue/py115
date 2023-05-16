__author__ = 'deadblue'

class Credential:
    """Credential contains required information to identify user.
    """

    _uid: str = None
    _cid: str = None
    _seid: str = None

    def __init__(self, uid: str = None, cid: str = None, seid: str = None) -> None:
        self._uid = uid
        self._cid = cid
        self._seid = seid

    @classmethod
    def from_dict(cls, d: dict):
        """Create Credential from a dict object.

        :param d: dict object.
        :type d: dict
        """
        if len(d) == 0 or not ('UID' in d and 'CID' in d and 'SEID' in d):
            return None
        return Credential(
            uid=d.get('UID'),
            cid=d.get('CID'),
            seid=d.get('SEID')
        )

    def to_dict(self) -> dict:
        """Convert Credential object to dict object.

        :return: dict object contains required information.
        :rtype: dict
        """
        return {
            'UID': self._uid,
            'CID': self._cid,
            'SEID': self._seid,
        }

    def __repr__(self) -> str:
        return f'UID={self._uid}, CID={self._cid}, SEID={self._seid}'
