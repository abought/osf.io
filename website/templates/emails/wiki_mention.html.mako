<% from website.models import User %>

<table class="comment-row" border="0" cellpadding="8" cellspacing="0" width="100%" align="center" style="font-size: 13px;background: #fff;border: 1px solid #eee;border-radius: 5px;margin-bottom: 10px;padding: 0px !important;">
    <tr>
        <td width="40" class="icon" valign="middle" style="border-collapse: collapse;font-size: 24px;color: #999;"> <img class="avatar" src="${gravatar_url}" width="48" alt="avatar" style="border: 0;height: auto;line-height: 100%;outline: none;text-decoration: none;border-radius: 25px;"> </td>
        <td style="line-height: 17px;border-collapse: collapse;">
            <span class="person" style="font-weight: bold;">${editor.fullname} </span>
            <span class="text"> mentioned you in the ${node_title}  </span>
            <span class="timestamp" style="color: grey;"> wiki page ${page_name} at ${localized_timestamp}</span>
        </td>
        <td class="link text-center" width="25" style="border-collapse: collapse;text-align: center;font-size: 18px;border-left: 1px solid #ddd;">
            <a href="${url}" style="padding: 0;margin: 0;border: none;list-style: none;color: #008de5;text-decoration: none;">&#10095;</a>
        </td>
    </tr>
</table>
