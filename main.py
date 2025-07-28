#                   route_info
# Trip No_ - Номер рейса - prefix: NSK, YR, YSP                                                             #
# Trip Date - Дата рейса                                                                                    #
# Source No_ - Номер заказа                                                                                 #
# Customer No_ - Код клиента                                                                                #
# Status - Статус Доставки - 0 или 4 - ожидает доставки,                                                    #
#                            1, 2    - отмена доставки,                                                     #
#                            5 - частична доставка                                                          #
#                            6 - доставлен полностью                                                        #
# Delivery Order Latitude - Широта |                                                                        #
#                                   > - координаты                                                          #
# Delivery Order Long - Долгота    |                                                                        #
# Delivery Time From - Интервал доставки с                                                                  #
# Delivery Time To - Интервал доставки по                                                                   #
# Delivery Fact Time - Фактическое время доставки - перевести в местно время из UTC to prefix(NSK, YR, YSP)
#
#                   track_info
# Latitude |
#          |->
# Longitude|
# Timestamp - дата вплоть до тысячных секунд
# RouteNumber - ignor
# DriveID - ignor
# RouteCode - Код рейса
# Accuracy - точность (иногда глючит)
# Speed - скорость (иногда глючит)
# PosDate - дата координаты
# IsGpsValid - ignor

print("helloworld")