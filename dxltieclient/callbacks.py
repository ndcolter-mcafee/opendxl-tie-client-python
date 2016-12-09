# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2016 McAfee Inc. - All Rights Reserved.
################################################################################

import json

from dxltieclient import TieClient
from dxlclient.callbacks import EventCallback
from constants import RepChangeEventProp, FileRepChangeEventProp, CertRepChangeEventProp


class ReputationChangeCallback(EventCallback):
    """
    Concrete instances of this class are used to receive "reputation change" messages from the TIE
    server when the `reputation` of files or certificates change.

    The following steps must be performed to create and register a reputation change callback
    (as shown in the example below):

        * Create a derived class from :class:`ReputationChangeCallback`
        * Override the :func:`on_reputation_change` method to handle reputation change events
        * Register the callback with the client:

            For files:
                :func:`dxltieclient.client.TieClient.add_file_reputation_change_callback`
            For certificates:
                :func:`dxltieclient.client.TieClient.add_certificate_reputation_change_callback`

    **Example Usage**

        .. code-block:: python

            class MyReputationChangeCallback(ReputationChangeCallback):
                def on_reputation_change(self, rep_change_dict, original_event):

                    # Dump the reputation change dictionary
                    print json.dumps(rep_change_dict,
                                     sort_keys=True, indent=4, separators=(',', ': '))

            # Create the client
            with DxlClient(config) as client:

                # Connect to the fabric
                client.connect()

                # Create the McAfee Threat Intelligence Exchange (TIE) client
                tie_client = TieClient(client)

                # Create reputation change callback
                rep_change_callback = MyReputationChangeCallback()

                # Register callback with client to receive file reputation change events
                tie_client.add_file_reputation_change_callback(rep_change_callback)
    """
    def on_event(self, event):
        """
        Invoked when a DXL event has been received.

        NOTE: This method should not be overridden (it performs transformations to simplify TIE usage).
        Instead, the :func:`on_reputation_change` method must be overridden.

        :param event: The :class:`dxlclient.message.Event` message that was received
        """
        # Decode the event payload
        rep_change_dict = json.loads(event.payload.decode(encoding="UTF-8"))

        # Transform hashes
        if RepChangeEventProp.HASHES in rep_change_dict:
            rep_change_dict[RepChangeEventProp.HASHES] = \
                TieClient._transform_hashes(rep_change_dict[RepChangeEventProp.HASHES])

        # Transform new reputations
        if RepChangeEventProp.NEW_REPUTATIONS in rep_change_dict:
            if "reputations" in rep_change_dict[RepChangeEventProp.NEW_REPUTATIONS]:
                rep_change_dict[RepChangeEventProp.NEW_REPUTATIONS] = \
                    TieClient._transform_reputations(
                        rep_change_dict[RepChangeEventProp.NEW_REPUTATIONS]["reputations"])

        # Transform old reputations
        if RepChangeEventProp.OLD_REPUTATIONS in rep_change_dict:
            if "reputations" in rep_change_dict[RepChangeEventProp.OLD_REPUTATIONS]:
                rep_change_dict[RepChangeEventProp.OLD_REPUTATIONS] = \
                    TieClient._transform_reputations(
                        rep_change_dict[RepChangeEventProp.OLD_REPUTATIONS]["reputations"])

        # Transform relationships
        if FileRepChangeEventProp.RELATIONSHIPS in rep_change_dict:
            relationships_dict = rep_change_dict[FileRepChangeEventProp.RELATIONSHIPS]
            if "certificate" in relationships_dict:
                cert_dict = relationships_dict["certificate"]
                if "hashes" in cert_dict:
                    cert_dict["hashes"] = \
                        TieClient._transform_hashes(cert_dict["hashes"])
                if "publicKeySha1" in cert_dict:
                    cert_dict["publicKeySha1"] = \
                        TieClient._base64_to_hex(cert_dict["publicKeySha1"])

        # Transform certificate public-key SHA-1 (if applicable)
        if CertRepChangeEventProp.PUBLIC_KEY_SHA1 in rep_change_dict:
            rep_change_dict[CertRepChangeEventProp.PUBLIC_KEY_SHA1] = \
                TieClient._base64_to_hex(rep_change_dict[CertRepChangeEventProp.PUBLIC_KEY_SHA1])

        # Invoke the reputation change method
        self.on_reputation_change(rep_change_dict, event)

    def on_reputation_change(self, rep_change_dict, original_event):
        """
        NOTE: This method must be overridden by derived classes.

        Each `reputation change event` that is received from the DXL fabric will cause this method to be
        invoked with the corresponding `reputation change information`.

        **Reputation Change Information**

            The `Reputation Change` information is provided as a Python ``dict`` (dictionary) via the
            ``rep_change_dict`` parameter.

            An example `reputation change` ``dict`` (dictionary) is shown below:

            .. code-block:: python

                {
                    "hashes": {
                        "md5": "f2c7bb8acc97f92e987a2d4087d021b1",
                        "sha1": "7eb0139d2175739b3ccb0d1110067820be6abd29",
                        "sha256": "142e1d688ef0568370c37187fd9f2351d7ddeda574f8bfa9b0fa4ef42db85aa2"
                    },
                    "newReputations": {
                        "1": {
                            "attributes": {
                                "2120340": "2139160704"
                            },
                            "createDate": 1480455704,
                            "providerId": 1,
                            "trustLevel": 99
                        },
                        "3": {
                            "attributes": {
                                "2101652": "235",
                                "2102165": "1476902802",
                                "2111893": "244",
                                "2114965": "4",
                                "2139285": "73183493944770750"
                            },
                            "createDate": 1476902802,
                            "providerId": 3,
                            "trustLevel": 99
                        }
                    },
                    "oldReputations": {
                        "1": {
                            "attributes": {
                                "2120340": "2139160704"
                            },
                            "createDate": 1480455704,
                            "providerId": 1,
                            "trustLevel": 99
                        },
                        "3": {
                            "attributes": {
                                "2101652": "235",
                                "2102165": "1476902802",
                                "2111893": "244",
                                "2114965": "4",
                                "2139285": "73183493944770750"
                            },
                            "createDate": 1476902802,
                            "providerId": 3,
                            "trustLevel": 85
                        }
                    },
                    "updateTime": 1481219581
                }

            The top level property names in the dictionary can be found in the following constants classes
            (which derive from the :class:`dxltieclient.constants.RepChangeEventProp` class):

                For files:
                    :class:`dxltieclient.constants.FileRepChangeEventProp`
                For certificates:
                    :class:`dxltieclient.constants.CertRepChangeEventProp`

            The `reputation change` information is separated into 4 distinct sections:

                **Hash values**

                    Keyed in the dictionary by the ``"hashes"`` string.

                    A ``dict`` (dictionary) of hashes that identify the file or certificate whose reputation has
                    changed. The ``key`` in the dictionary is the `hash type` and the ``value`` is the `hex`
                    representation of the hash value. See the :class:`dxltieclient.constants.HashType` class for the
                    list of `hash type` constants.

                    For certificates there may also be a top-level property named, ``"publicKeySha1"`` that
                    contains the SHA-1 of the certificate's public key.

                **New reputations**

                    Keyed in the dictionary by the ``"newReputations"`` string.

                    The new `Reputations` for the file or certificate whose reputation has changed as a
                    Python ``dict`` (dictionary).

                    The `key` for each entry in the ``dict`` (dictionary) corresponds to a particular `provider` of the
                    associated `reputation`. The list of `file reputation providers` can be found in the
                    :class:`dxltieclient.constants.FileProvider` constants class. The list of
                    `certificate reputation providers` can be found in the :class:`dxltieclient.constants.CertProvider`
                    constants class.

                    Each reputation contains a standard set of properties (trust level, creation date, etc.). These
                    properties are listed in the :class:`dxltieclient.constants.ReputationProp` constants class.

                    Each reputation can also contain a provider-specific set of attributes as a Python ``dict``
                    (dictionary). These attributes can be found in the :class:`dxltieclient.constants` module:

                        :class:`dxltieclient.constants.FileEnterpriseAttrib`
                            Attributes associated with the `Enterprise` reputation provider for files
                        :class:`dxltieclient.constants.FileGtiAttrib`
                            Attributes associated with the `Global Threat Intelligence (GTI)` reputation provider for
                            files
                        :class:`dxltieclient.constants.AtdAttrib`
                            Attributes associated with the `Advanced Threat Defense (ATD)` reputation provider
                        :class:`dxltieclient.constants.CertEnterpriseAttrib`
                            Attributes associated with the `Enterprise` reputation provider for certificates
                        :class:`dxltieclient.constants.CertGtiAttrib`
                            Attributes associated with the `Global Threat Intelligence (GTI)` reputation provider for
                            certificates

                **Old reputations**

                    Keyed in the dictionary by the ``"oldReputations"`` string.

                    The previous `Reputations` for the file or certificate whose reputation has changed as a
                    Python ``dict`` (dictionary).

                    See the "New reputations" section above for additional information regarding reputation
                    details.

                **Change time**

                    Keyed in the dictionary by the ``"updateTime"`` string.

                    The time the reputation change occurred (Epoch time).

        :param rep_change_dict: A Python ``dict`` (dictionary) containing the details of the reputation change
        :param original_event: The original DXL event message that was received
        """
        raise NotImplementedError("Must be implemented in a child class.")
