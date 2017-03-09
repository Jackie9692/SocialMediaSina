#coding=utf-8
import re
import sys
from geopy.geocoders import Baidu
from util import configReader
reload(sys)
sys.setdefaultencoding('utf8')
class validator():
    """
        validate the status comments user_profiles
    """
    def __init__(self):
        self.geoLocator = Baidu(configReader.getOptionValue('data_validation', 'baidu_map_ak'))

    def getAddressFromPoint(self, coordinates):
        """
         根据经纬度坐标信息获取详细的地理位置信息：省市、城市、详细位置信息
        """
        if coordinates:
            # 将经纬度坐标组成API接受的字符串格式
            coordinate = str(coordinates[0]) + ", " + str(coordinates[1])
            try:
                location = self.geoLocator.reverse(coordinate) #调用Baidu Map API解析坐标点
            except Exception, e:
                print e
            else:
                #获取坐标点对应的省市信息
                province = location.raw.get('addressComponent').get('province')
                city = location.raw.get('addressComponent').get('city')
                address = location.raw.get('formatted_address')
                return city, province, address
        else:
            return "", "", ""
    def getPoinFromFomattedAddress(self, address):
        """
        根据详细地址获取地理经纬度坐标信息
        """
        try:
            if address:
                location = self.geoLocator.geocode(address)
                if location:
                    coordinates = [location._point.latitude, location._point.longitude]
                    return coordinates
        except Exception, e:
            print e

    def validateSource(self, source_field):
        """
        source 字段处理：<a>sourceText</a>或者sourceText
        :param source_field:
        :return:soureText,sourceType
        """
        sourceTextList = re.findall(r'(?<=\>).*?(?=\<\/a\>)', source_field)  # 从<a></a>中获取source内容
        if sourceTextList:
            sourceText = sourceTextList[0]
        else:
            sourceText = source_field
        # decide the source type base on the sourceText
        sourceTypes = configReader.getOptionsValus("source_type")
        sourceType = None
        for source_type in sourceTypes:
            sourceTypeItems = configReader.getOptionsValus(source_type)
            for item in sourceTypeItems:
                if item in sourceText:
                    sourceType = source_type
                    break
            if sourceType != None:
                break
        if sourceType==None:
            sourceType="Others"
        return sourceText, sourceType
    def validateUserProfile(self,userAccount):
        """
        用户账户信息预处理
        """
        def validateUserURL():
            user_id = userAccount.user_id
            if user_id:
                url = "http://weibo.com/u/" + str(user_id) + '/home'
                return url
        return validateUserURL()

    def validateComment(self, comment):
        """
        :param comment:需要预处理的comment
        1.预处理comment的source字段
        """
        source_field = comment.source
        sourceText, source_type = self.validateSource(source_field)
        return sourceText, source_type

    def validateStatus(self, status):
        """
            微博数据预处理
            1.0
            statusurl字段：如果无此字段，添加此字段
            1.1
            地理信息字段；如果存在geo字段，可能是坐标点信息（API获取）或address字段（爬虫爬取）；否则设置为个字段为空字符串的默认值
            1.2
            Source字段：可能为链接形式（API获取），也可能是字符串形式（爬虫爬取）
            """
        geo_field = status.geo
        source_field = status.source
        def validateStatusURL(status): #验证status具有URL字段
            statusURL = status.statusurl
            if statusURL == None:
                user_id = status.user_simple.get('user_id')
                if user_id:
                    statusURL = "http://api.weibo.com/2/statuses/go?uid=" + str(user_id) + "&id=" + str(
                        status.status_id)
                    status.update(statusurl=statusURL)
                else:
                    statusURL = "http://www.weibo.com"
            return statusURL

        def validateGeo(geo_field):
            """
                Geo字段预处理
            """
            geo = {}
            geoDefault = {'city': "", 'province': "", "address": ""}
            if geo_field:
                    if geo_field.get("type") == "point":  # 坐标类型
                            city, province, address = self.getAddressFromPoint(geo_field.get('coordinates'))
                            geo['city'] = city
                            geo['province'] = province
                            geo['address'] = address
                    # 存在address,可能是已经验证过的，还有可能是Crawler爬到Merge的
                    elif geo_field.get("address") != None:
                            if geo_field.get("province") == None:  # 可断定为（crawler爬到的微博）
                                point = self.getPoinFromFomattedAddress(geo_field.get('address'))
                                if point:
                                    city, province, address = self.getAddressFromPoint(point)
                                    geo['city'] = city
                                    geo['province'] = province
                                    geo['address'] = address
                                else:
                                    geo=geoDefault
                            else:  # 已经验证过
                                geo = geo_field
            else:
                 geo=geoDefault
            return geo
        geo = validateGeo(geo_field)
        sourceText, sourceType = self.validateSource(source_field)
        statusURL = validateStatusURL(status)
        return geo, sourceText, sourceType, statusURL




