{% extends "mail_templated/base.tpl" %}

{% block subject %}
Please confirm your email address - Kleeppr
{% endblock %}

{% block html %}
<html xmlns="http://www.w3.org/1999/xhtml"
      style="font-family: sans-serif; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; font-size: 62.5%; -webkit-tap-highlight-color: rgba(0, 0, 0, 0);">
<head style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box;">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"
          style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box;"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"
          style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box;"/>


    <title style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box;">Kleeppr - discover newsletters you love, subscribe anonymously!</title>
</head>
<body style="margin: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; font-family: Helvetica Neue, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.428571429; color: #333333; background-color: #ffffff; padding: 20px; width: 100%; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">
<center style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box;">
    <table id="main" class="container-fluid"
           style="border-collapse: collapse; border-spacing: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; margin-right: auto; margin-left: auto; padding-left: 15px; padding-right: 15px; max-width: 600px; background-color: transparent; padding: 0; text-align: left;">
        <tr style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; vertical-align: top;">
            <td style="padding: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; border-collapse: collapse; text-align: center;">
                <h1 style="font-size: 24px; margin: 0.67em 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; font-family: inherit; font-weight: 500; line-height: 1.1; color: inherit; margin-top: 20px; margin-bottom: 10px;">
                                { Kleeppr }</h1>
                <h5 style="color:#6c757d">discover <font style="color:#da2d2d;">newsletters</font> you love, subscribe <font style="color:#da2d2d;">anonymously</font></h5>

            </td>
        </tr>

        <tr style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; vertical-align: top;">
            <td style="padding: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; border-collapse: collapse;">
                <!-- Content -->
                <table id="content"
                       style="border-collapse: collapse; border-spacing: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; max-width: 100%; background-color: transparent; text-align: left;">
                    <tr style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; vertical-align: top;">
                        <td style="padding: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; border-collapse: collapse;">

                            <p style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; margin: 30px 0 10px;">
                                Hey,
                               </p>
                            <p style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; margin: 0 0 30px;">
                                Welcome to Kleeppr. In order to get started, you need to confirm your email address.</p>
                            <a href="{{ url }}" class="btn btn-success btn-block"
                                           style="background: transparent; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; color: #ffffff; text-decoration: none; display: block;  margin-bottom: 40px; font-weight: normal; text-align: center; vertical-align: middle; cursor: pointer; background-image: none; border: 1px solid transparent; white-space: nowrap; padding: 6px 12px; font-size: 14px; line-height: 1.428571429; border-radius: 4px; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; background-color: #5cb85c; border-color: #4cae4c; width: 100%; padding-left: 0; padding-right: 0;">
                                <strong>Confirm Email</strong></a>

                              <p style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; margin: 0 0 5px;">
                               Thanks,</p>
                            <p style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; margin: 0 0 10px;">
                               The Kleeppr Team</p>

                        </td>
                    </tr>
                </table>
                <!-- /Content -->
            </td>
        </tr>

        <tr style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; vertical-align: top; ">
            <td style="padding: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; border-collapse: collapse;text-align: center;">
                <p style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; margin: 40px 0 10px;">
                                <small>Sent by kleeppr.com with &#9829; from California</small></p>
                <p style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; margin: 20px 0 10px;">
                                <small>&#9993; hello@kleeppr.com</small></p>

            </td>
        </tr>
    </table>
</center>
</body>
</html>

{% endblock %}