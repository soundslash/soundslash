__version__ = "0.2"

import tornado.web
import tornado.gen
import motor
import datetime
import base64
import StringIO
from PIL import Image
from bson.binary import Binary

class ThumbImage():

    def __init__(self):

        self.templates = {
            "default": { "data-100x100": [100, 100] },
            "profile": { "data-160x160": [160, 160],
                         "data-60x60": [65, 65],
                         "data-135x135": [135, 135],
                         "data-256x160": [256, 160],
                         "data-160x90": [160, 90] },
            "player-photos": { "data-300x300": [300, 300 ] },
            "player-cover": { "data-1440x555": [1440, 555 ], "data-1440x900": [1440, 900 ], "data-500x300": [500, 300], "data-332x128": [332, 128] }
        }

        self.max_size = [1440, 900]
        self.quality = 85

    def add_custom_template(self, width, height, force = False):
        if force:
            template = "custom-force"
        else:
            template = "custom"
        self.templates[template] = { "data-"+unicode(width)+"x"+unicode(height): [width, height] }

    def process(self, data, format="binary>binary", tags=[], attrs={}, template=None):
        allow = 0
        if template is not None:
            for temp, resize_data in self.templates.items():
                if temp == "custom": continue
                for name, size in resize_data.items():
                    size2 = self.templates[template].itervalues().next()
                    if size[0] == size2[0] and size[1] == size2[1]: allow = 1
        if not allow: raise Exception("Resize not allowed")


        if type(data) == Binary:
            data = str(data)


        format = format.split(">")
        self.from_format = format[0]
        self.to_format = format[1]

        if self.from_format == "json": data = self.__from_json(data)
        self.__raise_if_max_size_ratio_is_reached(data)


        # format: json/binary
        self.image = {
            "format": self.to_format,
            "template": template,
            "tags": tags,
            "created_at": datetime.datetime.utcnow()
        }
        self.image = dict(self.image.items() + attrs.items())

        data = self.__resize_min(data, self.max_size[0], self.max_size[1])
        if template is not None:
            for name, size in self.templates[template].items():
                thumb = self.__make_thumb(data, size[0], size[1])
                if self.to_format == "json": thumb = self.__to_json(thumb)
                self.image[name] = thumb


        if self.to_format == "json": self.image["data"] = self.__to_json(data)
        else: self.image["data"] = data

        if self.to_format == "binary":
            for key, value in self.image.items():
                if key.startswith("data"):
                    self.image[key] = Binary(value)

        return self.image


    def get_data(self, data, from_format, to_format):
        if to_format == "json": return self.__get_json(data, from_format)
        if to_format == "binary": return self.__get_binary(data, from_format)
        return None

    def __raise_if_max_size_ratio_is_reached(self, data):
        imageFile = StringIO.StringIO(data)

        im1 = Image.open(imageFile)

        width = float(float(im1.size[0])/float(im1.size[1]))
        height = float(float(im1.size[1])/float(im1.size[0]))

        if width > height:
            bigger = width
        else:
            bigger = height
        #     4 is the biggest panorama I had in my computer
        if bigger > 6: raise Exception("Not allowed: Max size ratio is reached ("+unicode(bigger)+")")


    def __resize_min(self, data, min_width, min_height, force = False):
        """
        Resized image has at least min_width and min_height pixels or original.
        """
        imageFile = StringIO.StringIO(data)

        im1 = Image.open(imageFile)

        result_width = min_width
        result_height = min_height

        # new size according width
        new_width = result_width
        new_height = int(im1.size[1]*result_width/im1.size[0])

        # is image bigger?
        if new_width < result_width or new_height < result_height:
            # new size according height
            new_width = int(im1.size[0]*result_height/im1.size[1])
            new_height = result_height

        if force:
            im1 = im1.resize((new_width, new_height), Image.ANTIALIAS)
        else:
            if min_width >= im1.size[0] or min_height >= im1.size[1]:
                # Not resize, image is not enaugh big
                pass
            else:
                im1 = im1.resize((new_width, new_height), Image.ANTIALIAS)

        output = StringIO.StringIO()
        im1.save(output, format="JPEG", quality=self.quality)
        new_data = output.getvalue()
        output.close()
        return new_data


    def __make_thumb(self, data, width=500, height=500):
        imageFile = StringIO.StringIO(data)

        im1 = Image.open(imageFile)

        result_width = width
        result_height = height

        # new size according width
        new_width = result_width
        new_height = int(im1.size[1]*result_width/im1.size[0])

        # is image bigger?
        if new_width < result_width or new_height < result_height:
            # new size according height
            new_width = int(im1.size[0]*result_height/im1.size[1])
            new_height = result_height

        im1 = im1.resize((new_width, new_height), Image.ANTIALIAS)

        # by width
        if result_width == new_width:
            top = int(new_height/2-result_height/2)
            box = (0, top, result_width, result_height+top)
        else:
            left = int(new_width/2-result_width/2)
            box = (left, 0, left+result_width, result_height)

        im1 = im1.crop(box)

        output = StringIO.StringIO()
        im1.save(output, format="JPEG", quality=self.quality)
        new_data = output.getvalue()
        output.close()
        return new_data


    def __get_binary(self, data, format):
        if format == "json":
            return self.__from_json(data)
        else:
            return data

    def __get_json(self, data, format):
        if format == "json":
            return data
        else:
            return self.__to_json(data)

    def __to_json(self, data):
        return "data:image/jpeg;base64,"+base64.b64encode(str(data))

    def __from_json(self, data):
        content_type, image_b64 = self.__parse_json_data(data)
        return str(base64.b64decode(image_b64))

    def __parse_json_data(self, data):
        image = data.split(",")
        head = image[0]
        del image[0]
        image_b64 = ",".join(image)
        content_type = head.split(";")[0].split(":")[1]
        return content_type, image_b64
