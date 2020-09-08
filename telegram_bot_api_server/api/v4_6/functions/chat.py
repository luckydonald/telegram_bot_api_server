#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union, Optional

from fastapi import Query, HTTPException
from fastapi import APIRouter as Blueprint
from luckydonaldUtils.logger import logging

__author__ = 'luckydonald'

from telethon.errors import BotMethodInvalidError
from telethon.tl.types import ChannelParticipantsAdmins

from ....api.v4_6.generated.models import ChatPermissionsModel, InputFileModel
from ....tools.fastapi_issue_884_workaround import Json, parse_obj_as
from ....constants import TOKEN_VALIDATION
from ....serializer import get_entity, to_web_api
from ....tools.responses import JSONableResponse, r_success

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.add_colored_handler(level=logging.DEBUG)
# end if

# noinspection PyUnresolvedReferences
__all__ = [
    'kick_chat_member', 'unban_chat_member', 'restrict_chat_member', 'promote_chat_member', 'set_chat_administrator_custom_title',
    'set_chat_permissions', 'export_chat_invite_link', 'delete_chat_photo', 'set_chat_title', 'set_chat_description',
    'pin_chat_message', 'unpin_chat_message', 'leave_chat',
    'get_chat', 'get_chat_administrators', 'get_chat_members_count', 'get_chat_member',
    'set_chat_sticker_set', 'delete_chat_sticker_set',
]

routes = Blueprint()  # APIRouter is basically a Blueprint


def new_edit_permissions(bot, entity, user, until_date, permissions: ChatPermissionsModel):
    try:
        result = await bot.edit_permissions(
            entity=entity,
            user=user,  # is chat default
            until_date=None,  # is chat default
            view_messages = True,
            send_messages = permissions.can_send_messages,
            send_media = permissions.can_send_media_messages,
            send_stickers = permissions.can_send_other_messages,
            send_gifs = permissions.can_send_other_messages,
            send_games = permissions.can_send_other_messages,
            send_inline = permissions.can_send_other_messages,
            send_polls = permissions.can_send_polls,
            change_info = permissions.can_change_info,
            invite_users = permissions.can_invite_users,
            pin_messages = permissions.can_pin_messages,
            embed_links = permissions.can_add_web_page_previews,
        )
        logger.warning('It worked, so telethon was updated? Maintainer, remove compatibility workaround, pls.')
    except TypeError:

        from telethon import helpers
        from telethon.tl import types
        from telethon.tl import functions

        entity = entity
        view_messages = True
        send_messages = permissions.can_send_messages
        send_media = permissions.can_send_media_messages
        send_stickers = permissions.can_send_other_messages
        send_gifs = permissions.can_send_other_messages
        send_games = permissions.can_send_other_messages
        send_inline = permissions.can_send_other_messages
        send_polls = permissions.can_send_polls
        change_info = permissions.can_change_info
        invite_users = permissions.can_invite_users
        pin_messages = permissions.can_pin_messages
        embed_links = permissions.can_add_web_page_previews

        entity=await bot.get_input_entity(entity)
        ty = helpers._entity_type(entity)
        if ty != helpers._EntityType.CHANNEL:
            raise ValueError('You must pass either a channel or a supergroup')

        rights = types.ChatBannedRights(
            until_date=until_date,
            view_messages=not view_messages,
            send_messages=not send_messages,
            send_media=not send_media,
            send_stickers=not send_stickers,
            send_gifs=not send_gifs,
            send_games=not send_games,
            send_inline=not send_inline,
            send_polls=not send_polls,
            change_info=not change_info,
            invite_users=not invite_users,
            pin_messages=not pin_messages,
            embed_links=not embed_links,
        )

        if user is None:
            return await bot(functions.messages.EditChatDefaultBannedRightsRequest(
                peer=entity,
                banned_rights=rights
            ))

        user = await bot.get_input_entity(user)
        ty = helpers._entity_type(user)
        if ty != helpers._EntityType.USER:
            raise ValueError('You must pass a user entity')

        if isinstance(user, types.InputPeerSelf):
            raise ValueError('You cannot restrict yourself')

        result = await bot(functions.channels.EditBannedRequest(
            channel=entity,
            user_id=user,
            banned_rights=rights
        ))
    # end try

@routes.api_route('/{token}/kickChatMember', methods=['GET', 'POST'], tags=['official', 'chats'])
async def kick_chat_member(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target group or username of the target supergroup or channel (in the format @channelusername)'),
    user_id: int = Query(..., description='Unique identifier of the target user'),
    until_date: Optional[int] = Query(None, description='Date when the user will be unbanned, unix time. If user is banned for more than 366 days or less than 30 seconds from the current time they are considered to be banned forever'),
) -> JSONableResponse:
    """
    Use this method to kick a user from a group, a supergroup or a channel. In the case of supergroups and channels, the user will not be able to return to the group on their own using invite links, etc., unless unbanned first. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.

    https://core.telegram.org/bots/api#kickchatmember
    """

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    result = await bot.edit_permissions(
        entity=entity,
        user=user_id,
        view_messages=False,
        until_date=until_date,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


def __ignore__():
    @routes.api_route('/{token}/unbanChatMember', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def unban_chat_member(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target group or username of the target supergroup or channel (in the format @username)'),
        user_id: int = Query(..., description='Unique identifier of the target user'),
    ) -> JSONableResponse:
        """
        Use this method to unban a previously kicked user in a supergroup or channel. The user will not return to the group or channel automatically, but will be able to join via link, etc. The bot must be an administrator for this to work. Returns True on success.

        https://core.telegram.org/bots/api#unbanchatmember
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.edit_permissions(
            entity=entity,
            user=user_id,
            view_messages=True,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


@routes.api_route('/{token}/restrictChatMember', methods=['GET', 'POST'], tags=['official', 'chats'])
async def restrict_chat_member(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)'),
    user_id: int = Query(..., description='Unique identifier of the target user'),
    permissions: Json['ChatPermissionsModel'] = Query(..., description='New user permissions'),
    until_date: Optional[int] = Query(None, description='Date when restrictions will be lifted for the user, unix time. If user is restricted for more than 366 days or less than 30 seconds from the current time, they are considered to be restricted forever'),
) -> JSONableResponse:
    """
    Use this method to restrict a user in a supergroup. The bot must be an administrator in the supergroup for this to work and must have the appropriate admin rights. Pass True for all permissions to lift restrictions from a user. Returns True on success.

    https://core.telegram.org/bots/api#restrictchatmember
    """
    permissions: ChatPermissionsModel = parse_obj_as(
        ChatPermissionsModel,
        obj=permissions,
    )

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    result = await new_edit_permissions(
        bot,
        entity=entity,
        user=user_id,
        until_date=until_date,
        permissions=permissions,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


def __ignore__():
    @routes.api_route('/{token}/promoteChatMember', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def promote_chat_member(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
        user_id: int = Query(..., description='Unique identifier of the target user'),
        can_change_info: Optional[bool] = Query(None, description='Pass True, if the administrator can change chat title, photo and other settings'),
        can_post_messages: Optional[bool] = Query(None, description='Pass True, if the administrator can create channel posts, channels only'),
        can_edit_messages: Optional[bool] = Query(None, description='Pass True, if the administrator can edit messages of other users and can pin messages, channels only'),
        can_delete_messages: Optional[bool] = Query(None, description='Pass True, if the administrator can delete messages of other users'),
        can_invite_users: Optional[bool] = Query(None, description='Pass True, if the administrator can invite new users to the chat'),
        can_restrict_members: Optional[bool] = Query(None, description='Pass True, if the administrator can restrict, ban or unban chat members'),
        can_pin_messages: Optional[bool] = Query(None, description='Pass True, if the administrator can pin messages, supergroups only'),
        can_promote_members: Optional[bool] = Query(None, description='Pass True, if the administrator can add new administrators with a subset of their own privileges or demote administrators that he has promoted, directly or indirectly (promoted by administrators that were appointed by him)'),
    ) -> JSONableResponse:
        """
        Use this method to promote or demote a user in a supergroup or a channel. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Pass False for all boolean parameters to demote a user. Returns True on success.

        https://core.telegram.org/bots/api#promotechatmember
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.promote_chat_member(
            entity=entity,
            user_id=user_id,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_pin_messages=can_pin_messages,
            can_promote_members=can_promote_members,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


@routes.api_route('/{token}/setChatAdministratorCustomTitle', methods=['GET', 'POST'], tags=['official', 'chats'])
async def set_chat_administrator_custom_title(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)'),
    user_id: int = Query(..., description='Unique identifier of the target user'),
    custom_title: str = Query(..., description='New custom title for the administrator; 0-16 characters, emoji are not allowed'),
) -> JSONableResponse:
    """
    Use this method to set a custom title for an administrator in a supergroup promoted by the bot. Returns True on success.

    https://core.telegram.org/bots/api#setchatadministratorcustomtitle
    """

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    result = await bot.edit_admin(
        entity=entity,
        user=user_id,
        title=custom_title,
    )
    # data = await to_web_api(result, bot)
    return r_success(True)
# end def


@routes.api_route('/{token}/setChatPermissions', methods=['GET', 'POST'], tags=['official', 'chats'])
async def set_chat_permissions(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)'),
    permissions: Json['ChatPermissionsModel'] = Query(..., description='New default chat permissions'),
) -> JSONableResponse:
    """
    Use this method to set default chat permissions for all members. The bot must be an administrator in the group or a supergroup for this to work and must have the can_restrict_members admin rights. Returns True on success.

    https://core.telegram.org/bots/api#setchatpermissions
    """
    permissions: ChatPermissionsModel = parse_obj_as(
        ChatPermissionsModel,
        obj=permissions,
    )

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    _

    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


def __ingnored__():
    @routes.api_route('/{token}/exportChatInviteLink', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def export_chat_invite_link(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    ) -> JSONableResponse:
        """
        Use this method to generate a new invite link for a chat; any previously generated link is revoked. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns the new invite link as String on success.

        Note: Each administrator in a chat generates their own invite links. Bots can't use invite links generated by other administrators. If you want your bot to work with invite links, it will need to generate its own link using exportChatInviteLink — after this the link will become available to the bot via the getChat method. If your bot needs to generate a new invite link replacing its previous one, use exportChatInviteLink again.


        https://core.telegram.org/bots/api#exportchatinvitelink
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.chat(
            entity=entity,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def
# end def

def __ignored__():
    @routes.api_route('/{token}/setChatPhoto', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def set_chat_photo(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
        photo: Json['InputFileModel'] = Query(..., description='New chat photo, uploaded using multipart/form-data'),
    ) -> JSONableResponse:
        """
        Use this method to set a new profile photo for the chat. Photos can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.

        https://core.telegram.org/bots/api#setchatphoto
        """
        photo: InputFileModel = parse_obj_as(
            InputFileModel,
            obj=photo,
        )

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.set_chat_photo(
            entity=entity,
            photo=photo,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


def __ignored__():
    @routes.api_route('/{token}/deleteChatPhoto', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def delete_chat_photo(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    ) -> JSONableResponse:
        """
        Use this method to delete a chat photo. Photos can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.

        https://core.telegram.org/bots/api#deletechatphoto
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.delete_chat_photo(
            entity=entity,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def

def __later__():
    @routes.api_route('/{token}/setChatTitle', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def set_chat_title(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
        title: str = Query(..., description='New chat title, 1-255 characters'),
    ) -> JSONableResponse:
        """
        Use this method to change the title of a chat. Titles can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.

        https://core.telegram.org/bots/api#setchattitle
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.edit_permissions(
            entity=entity,
            title=title,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


def __later__():
    @routes.api_route('/{token}/setChatDescription', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def set_chat_description(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
        description: Optional[str] = Query(None, description='New chat description, 0-255 characters'),
    ) -> JSONableResponse:
        """
        Use this method to change the description of a group, a supergroup or a channel. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.

        https://core.telegram.org/bots/api#setchatdescription
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.set_chat_description(
            entity=entity,
            description=description,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


@routes.api_route('/{token}/pinChatMessage', methods=['GET', 'POST'], tags=['official', 'chats'])
async def pin_chat_message(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
    message_id: int = Query(..., description='Identifier of a message to pin'),
    disable_notification: Optional[bool] = Query(None, description='Pass True, if it is not necessary to send a notification to all chat members about the new pinned message. Notifications are always disabled in channels.'),
) -> JSONableResponse:
    """
    Use this method to pin a message in a group, a supergroup, or a channel. The bot must be an administrator in the chat for this to work and must have the ‘can_pin_messages’ admin right in the supergroup or ‘can_edit_messages’ admin right in the channel. Returns True on success.

    https://core.telegram.org/bots/api#pinchatmessage
    """

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    result = await bot.pin_message(
        entity=entity,
        message=message_id,
        notify=not disable_notification,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


@routes.api_route('/{token}/unpinChatMessage', methods=['GET', 'POST'], tags=['official', 'chats'])
async def unpin_chat_message(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target channel (in the format @channelusername)'),
) -> JSONableResponse:
    """
    Use this method to unpin a message in a group, a supergroup, or a channel. The bot must be an administrator in the chat for this to work and must have the ‘can_pin_messages’ admin right in the supergroup or ‘can_edit_messages’ admin right in the channel. Returns True on success.

    https://core.telegram.org/bots/api#unpinchatmessage
    """

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    result = await bot.pin_message(
        entity=entity,
        message=None,
        notify=False,
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def


@routes.api_route('/{token}/leaveChat', methods=['GET', 'POST'], tags=['official', 'chats'])
async def leave_chat(
    token: str = TOKEN_VALIDATION,
    chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup or channel (in the format @channelusername)'),
) -> JSONableResponse:
    """
    Use this method for your bot to leave a group, supergroup or channel. Returns True on success.

    https://core.telegram.org/bots/api#leavechat
    """

    from ....main import _get_bot
    bot = await _get_bot(token)

    try:
        entity = await get_entity(bot, chat_id)
    except BotMethodInvalidError:
        assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
        entity = chat_id
    except ValueError:
        raise HTTPException(404, detail="chat not found?")
    # end try

    result = await bot.kick_participant(
        entity=entity,
        user='me',
    )
    data = await to_web_api(result, bot)
    return r_success(data.to_array())
# end def

def __later_i_guess__():
    @routes.api_route('/{token}/getChat', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def get_chat(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup or channel (in the format @channelusername)'),
    ) -> JSONableResponse:
        """
        Use this method to get up to date information about the chat (current name of the user for one-on-one conversations, current username of a user, group or channel, etc.). Returns a Chat object on success.

        https://core.telegram.org/bots/api#getchat
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.get_me(
            entity=entity,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


def __later__():
    @routes.api_route('/{token}/getChatAdministrators', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def get_chat_administrators(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup or channel (in the format @channelusername)'),
    ) -> JSONableResponse:
        """
        Use this method to get a list of administrators in a chat. On success, returns an Array of ChatMember objects that contains information about all chat administrators except other bots. If the chat is a group or a supergroup and no administrators were appointed, only the creator will be returned.

        https://core.telegram.org/bots/api#getchatadministrators
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        # https://t.me/TelethonChat/248256
        result = await bot.iter_participants(
            entity=entity,
            filter=ChannelParticipantsAdmins()
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


def __later__():
    @routes.api_route('/{token}/getChatMembersCount', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def get_chat_members_count(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup or channel (in the format @channelusername)'),
    ) -> JSONableResponse:
        """
        Use this method to get the number of members in a chat. Returns Int on success.

        https://core.telegram.org/bots/api#getchatmemberscount
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        # https://t.me/TelethonChat/248260
        # ((await client.get_participants(chat, limit=0)).total
        # which is sending
        # (await client(functions.channels.GetFullChannelRequest(entity))).full_chat.participants_count
        result = await bot.get_participants(
            entity=entity,
            limit=0,
        ).total
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


def __later__():
    @routes.api_route('/{token}/getChatMember', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def get_chat_member(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup or channel (in the format @channelusername)'),
        user_id: int = Query(..., description='Unique identifier of the target user'),
    ) -> JSONableResponse:
        """
        Use this method to get information about a member of a chat. Returns a ChatMember object on success.

        https://core.telegram.org/bots/api#getchatmember
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.get_chat_member(
            entity=entity,
            user_id=user_id,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


def __later__():
    @routes.api_route('/{token}/setChatStickerSet', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def set_chat_sticker_set(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)'),
        sticker_set_name: str = Query(..., description='Name of the sticker set to be set as the group sticker set'),
    ) -> JSONableResponse:
        """
        Use this method to set a new group sticker set for a supergroup. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Use the field can_set_sticker_set optionally returned in getChat requests to check if the bot can use this method. Returns True on success.

        https://core.telegram.org/bots/api#setchatstickerset
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.set_chat_sticker_set(
            entity=entity,
            sticker_set_name=sticker_set_name,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def


def __later__():
    @routes.api_route('/{token}/deleteChatStickerSet', methods=['GET', 'POST'], tags=['official', 'chats'])
    async def delete_chat_sticker_set(
        token: str = TOKEN_VALIDATION,
        chat_id: Union[int, str] = Query(..., description='Unique identifier for the target chat or username of the target supergroup (in the format @supergroupusername)'),
    ) -> JSONableResponse:
        """
        Use this method to delete a group sticker set from a supergroup. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Use the field can_set_sticker_set optionally returned in getChat requests to check if the bot can use this method. Returns True on success.

        https://core.telegram.org/bots/api#deletechatstickerset
        """

        from ....main import _get_bot
        bot = await _get_bot(token)

        try:
            entity = await get_entity(bot, chat_id)
        except BotMethodInvalidError:
            assert isinstance(chat_id, int) or (isinstance(chat_id, str) and len(chat_id) > 0 and chat_id[0] == '@')
            entity = chat_id
        except ValueError:
            raise HTTPException(404, detail="chat not found?")
        # end try

        result = await bot.delete_chat_sticker_set(
            entity=entity,
        )
        data = await to_web_api(result, bot)
        return r_success(data.to_array())
    # end def
