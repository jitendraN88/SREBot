# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import json

from typing import List
from botbuilder.core import CardFactory, TurnContext, MessageFactory
from botbuilder.core.teams import TeamsActivityHandler, TeamsInfo
from botbuilder.schema import Attachment, AttachmentData, CardAction, HeroCard, Mention, ConversationParameters, CardImage, Activity, ActivityTypes
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from botbuilder.schema._connector_client_enums import ActionTypes
from .splunk_operations import SplunkOperations 
from .utils import Utils
import asyncio

splunk = SplunkOperations()
utils = Utils()
ADAPTIVECARDTEMPLATE = "resources/SplunkStats.json"
GRAPHADAPTIVECARDTEMPLATE = "resources/graph.json"
STABILITYCARDTEMPLATE = "resources/aggregatedValue.json"


# ADAPTIVECARDTEMPLATE = "resources/UserMentionCardTemplate.json"

class TeamsConversationBot(TeamsActivityHandler):
    def __init__(self, app_id: str, app_password: str):
        self._app_id = app_id
        self._app_password = app_password

    async def on_teams_members_added(  # pylint: disable=unused-argument
            self,
            teams_members_added: [TeamsChannelAccount],
            team_info: TeamInfo,
            turn_context: TurnContext,
    ):
        for member in teams_members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome to the team {member.given_name} {member.surname}. "
                )

    async def on_message_activity(self, turn_context: TurnContext):
        TurnContext.remove_recipient_mention(turn_context.activity)
        text = turn_context.activity.text.strip().lower()
        # print("timeframe is ---"+text)
        # if turn_context.activity.text is not None: text = turn_context.activity.text.strip().lower()
        # else:
        #         text = turn_context.activity.value['action']
        #         print("text from teams is ---", turn_context.activity.value['action']) 
        
        if "|path" in text:
            print("text from teams is ---", text.split("|path")[0]) 
            # await self._get_path_statistics(turn_context, text)
            return
        
        if "|time" in text and "/" in text:
            await self._get_path_statistics(turn_context, text)
            return

        if "gettrends" in text:
            print("get trend is=="+text)
            await self._get_path_statistics_timeframe(turn_context, text)
            return

        if text.endswith(".com"):
            # await self._get_path_statistics_timeframe(turn_context, text)
            return

        if "|time" in text:
            if(os.path.isfile("os.path.isfile(path)")):
                os.remove("resources/graphnew1.png")
                
            await self.async_func(turn_context, text)
            # await self._mention_adaptive_card_activity(turn_context, text)
            # await self._get_path_statistics_graph(turn_context,text)
            return

        if "mention" in text:
            await self._mention_activity(turn_context)
            return

        if "update" in text:
            print("text is---",text)
            await self._send_card(turn_context, False)
            return

        if "message" in text:
            await self._message_all_members(turn_context)
            return

        if "who" in text:
            await self._get_member(turn_context)
            return

        if "delete" in text:
            await self._delete_card_activity(turn_context)
            return

        if "getincidents" in text:
            await self._send_incident_card(turn_context, False)
            return
        
        if "get4xx" in text:
            await self._send_incident_card_4xx(turn_context, False)
            return
        
        if "getincidenttrends" in text:
            await self._send_incident_card_trends(turn_context, False)
            return

        await self._send_select_region_card(turn_context, False)
        return

    async def async_func(self, turn_context:TurnContext, text):
        await self._mention_adaptive_card_activity(turn_context, text)
        await self._get_path_statistics_graph(turn_context,text)
    
    async def _mention_adaptive_card_activity(self, turn_context: TurnContext, text):
        print("search path 00 is:",text)
        
        trend = str(text).split("|")
        ch = "stability"
        
        if ch in trend[1]:
            card_path = os.path.join(os.getcwd(), STABILITYCARDTEMPLATE)
            splunk_result = splunk.desgin_splunk_output_stability(text)
        else:
            card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATE)
            splunk_result = splunk.desgin_splunk_output(text)
        
        with open(card_path, "rb") as in_file:
            template_json = json.load(in_file)
        
        template_json['body'][0]["rows"] = template_json['body'][0]["rows"] + splunk_result["message"]
        adaptive_card_attachment = Activity(
            text="",
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(template_json)]
        )
        await turn_context.send_activity(adaptive_card_attachment)
        #splunk_oneshotsearch_path_graph

    async def _mention_activity(self, turn_context: TurnContext):
        mention = Mention(
            mentioned=turn_context.activity.from_property,
            text=f"<at>{turn_context.activity.from_property.name}</at>",
            type="mention",
        )

        reply_activity = MessageFactory.text(f"Hello {mention.text}")
        reply_activity.entities = [Mention().deserialize(mention.serialize())]
        await turn_context.send_activity(reply_activity)
    
    async def _send_select_region_card(self, turn_context: TurnContext, isUpdate):
        buttons = [
            CardAction(
                type=ActionTypes.message_back, title="North America", text="getincidents|North America"
            ),
            CardAction(
                 type=ActionTypes.message_back, title="APAC", text="getincidents|APAC"
            ),
            CardAction(
                 type=ActionTypes.message_back, title="Europe", text="getincidents|Europe"
            )
        ]
        if isUpdate:
            await self._send_update_card(turn_context, buttons)
        else:
            await self._send_welcome_card(turn_context, buttons)
    
    async def _send_card(self, turn_context: TurnContext, isUpdate):
        text = turn_context.activity.text.split("|")[1]
        buttons = [
            CardAction(
                type=ActionTypes.message_back, title="Akamai", text="getincidenttrends|Akamai|"+text
            ),
            CardAction(
                type=ActionTypes.message_back, title="Moovweb", text="getincidenttrends|Moovweb|"+text
            ),
            CardAction(
                type=ActionTypes.message_back, title="SFCC", text="getincidenttrends|SFCC|"+text
            ),
        ]
        if isUpdate:
            await self._send_update_card(turn_context, buttons)
        else:
            await self._send_welcome_card(turn_context, buttons, titleMsg="Hosts")

    async def _send_incident_card_trends(self, turn_context: TurnContext, isUpdate):
        _context = turn_context.activity.text
        trend_name = _context.split("|")[1]
        buttons = []
        if trend_name == 'Akamai':
            path = utils.getRequestPath(_context.split("|")[2])
            request_path = path['Request_host']
            print("path data is----"+request_path)
            buttons = [
            CardAction(
                type=ActionTypes.message_back, title="Stability", text="gettrends|"+request_path+"|Stability"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Errors (4XX)", text="gettrends|"+request_path+"|Errors (4XX)"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Errors (5XX)", text="gettrends|"+request_path+"|Errors (5XX)"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Maintenance Page Trend", text="gettrends|"+request_path+"|Maintenance Page Trend"
            )
         ]
        elif trend_name == 'Moovweb':
          buttons = [
            CardAction(
                type=ActionTypes.message_back, title="Stability", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Latency", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Errors (4XX)", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Errors (5XX)", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Whoops Page Trend", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="PDP Errors", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="PLP Errors", text="gettrends"
            )
         ]
        elif trend_name == 'SFCC':
            buttons = [
            CardAction(
                type=ActionTypes.message_back, title="Stability", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Latency", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Errors (4XX)", text="gettrends"
            ),
            CardAction(
                type=ActionTypes.message_back, title="Errors (5XX)", text="gettrends"
            )
         ] 
        if isUpdate:
            await self._send_update_card(turn_context, buttons)
        else:
            await self._send_welcome_card(turn_context, buttons, titleMsg="Show Incident Trends")

    async def _send_incident_card(self, turn_context: TurnContext, isUpdate):
        region_slected_text= turn_context.activity.text.split("|")[1]
        region_label_list = utils.getLabel(turn_context.activity.text.split("|")[1])
        buttons = []
        for label in region_label_list:
           buttons.append(CardAction(
                type=ActionTypes.message_back, title=label, text="update|"+label+"|"+region_slected_text))
        
        if isUpdate:
            await self._send_update_card(turn_context, buttons, titleMsg="Platforms")
        else:
            await self._send_welcome_card(turn_context, buttons, titleMsg="Onboarded Hosts")
            
    # async def _send_incident_card_4xx(self, turn_context: TurnContext, isUpdate):
    #     buttons = [
    #         CardAction(
    #             type=ActionTypes.message_back,
    #             title="coachoutlet4xx.com",
    #             text="coachoutlet4xx.com",
    #         ),
    #     ]
    #     if isUpdate:
    #         await self._send_update_card(turn_context, buttons)
    #     else:
    #         await self._send_welcome_card(turn_context, buttons, titleMsg="Onboarded Hosts")       
            

    async def _send_welcome_card(self, turn_context: TurnContext, buttons, titleMsg="Welcome"):
        if "Card" in titleMsg:
            buttons.append(
                CardAction(
                    type=ActionTypes.message_back,
                    title="Update Card",
                    text="updatecardaction",
                    value={"count": 0},
                )
            )
        card = HeroCard(
            title=titleMsg, text="Click the buttons.", buttons=buttons
        )
        await turn_context.send_activity(
            MessageFactory.attachment(CardFactory.hero_card(card))
        )

    async def _send_update_card(self, turn_context: TurnContext, buttons):
        data = turn_context.activity.value
        data["count"] += 1
        buttons.append(
            CardAction(
                type=ActionTypes.message_back,
                title="Update Card",
                text="updatecardaction",
                value=data,
            )
        )
        card = HeroCard(
            title="Updated card", text=f"Update count {data['count']}", buttons=buttons
        )

        updated_activity = MessageFactory.attachment(CardFactory.hero_card(card))
        updated_activity.id = turn_context.activity.reply_to_id
        await turn_context.update_activity(updated_activity)

    async def _get_path_statistics_timeframe(self, turn_context: TurnContext, path):
        # path_value = path[0]['Request_host']
        path_arr= turn_context.activity.text.split("|")
        print("path value is 0=="+path_arr[1])
        print("path value is====="+path_arr[2])
        buttons = [
            CardAction(type=ActionTypes.message_back, title="15mins", text=path_arr[1]+"|"+path_arr[2] + "|time-15m"),
            CardAction(type=ActionTypes.message_back, title="30mins", text=path_arr[1]+"|"+path_arr[2]  + "|time-30m"),
            CardAction(type=ActionTypes.message_back, title="1 Hour", text=path_arr[1]+"|"+path_arr[2]  + "|time-1h"),
            CardAction(type=ActionTypes.message_back, title="4 Hours", text=path_arr[1]+"|"+path_arr[2]  + "|time-4h")
        ]
        await self._send_welcome_card(turn_context, buttons, titleMsg="Please select the timeframe.")

    async def _get_path_statistics_graph(self, turn_context: TurnContext, path):
        print("search path 0 is:",path)
        card_path = os.path.join(os.getcwd(), GRAPHADAPTIVECARDTEMPLATE)
        with open(card_path, "rb") as in_file:
            template_json = json.load(in_file)

        splunk_result = splunk.splunk_oneshotsearch_path_graph(path)
        template_json["body"][0]["url"] = str(splunk_result)

        adaptive_card_attachment = Activity(
            text="",
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(template_json)]
        )
        await turn_context.send_activity(adaptive_card_attachment)

    async def _get_path_statistics(self, turn_context: TurnContext, path):
        print(path)
        card_path = os.path.join(os.getcwd(), GRAPHADAPTIVECARDTEMPLATE)
        with open(card_path, "rb") as in_file:
            template_json = json.load(in_file)

        print("splunk result is--")
        splunk_result = splunk.get_graph_timewise_stats_for_path(path)
        print("splunk result is1--", splunk_result)
        template_json["body"][0]["url"] = str(splunk_result)

        adaptive_card_attachment = Activity(
            text="",
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(template_json)]
        )
        print("url is----------"+adaptive_card_attachment)
        await turn_context.send_activity(adaptive_card_attachment)

    async def _message_all_members(self, turn_context: TurnContext):
        team_members = await self._get_paged_members(turn_context)

        for member in team_members:
            conversation_reference = TurnContext.get_conversation_reference(
                turn_context.activity
            )

            conversation_parameters = ConversationParameters(
                is_group=False,
                bot=turn_context.activity.recipient,
                members=[member],
                tenant_id=turn_context.activity.conversation.tenant_id,
            )

            async def get_ref(tc1):
                conversation_reference_inner = TurnContext.get_conversation_reference(
                    tc1.activity
                )
                return await tc1.adapter.continue_conversation(
                    conversation_reference_inner, send_message, self._app_id
                )

            async def send_message(tc2: TurnContext):
                return await tc2.send_activity(
                    f"Hello {member.name}. I'm a Teams conversation bot."
                )  # pylint: disable=cell-var-from-loop

            await turn_context.adapter.create_conversation(
                conversation_reference, get_ref, conversation_parameters
            )

        await turn_context.send_activity(
            MessageFactory.text("All messages have been sent")
        )

    async def _get_paged_members(
            self, turn_context: TurnContext
    ) -> List[TeamsChannelAccount]:
        paged_members = []
        continuation_token = None

        while True:
            current_page = await TeamsInfo.get_paged_members(
                turn_context, continuation_token, 100
            )
            continuation_token = current_page.continuation_token
            paged_members.extend(current_page.members)

            if continuation_token is None:
                break

        return paged_members

    async def _delete_card_activity(self, turn_context: TurnContext):
        await turn_context.delete_activity(turn_context.activity.reply_to_id)

    async def _get_incident_activity(self, turn_context: TurnContext):
        await turn_context.send_activity(
            MessageFactory.text("Didn't get details for the incident.")
        )
