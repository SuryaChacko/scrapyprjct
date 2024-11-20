import scrapy


class BlogSpider(scrapy.Spider):
    name = 'DubaiProperties'
    start_urls = ['https://www.bayut.com/to-rent/property/dubai/']

    def parse(self, response):
        for property in response.css('a.d40f2294'):
            title = property.attrib.get('title')  # Extract title attribute
            link = property.attrib.get('href')    # Extract href attribute
            
            if link:
                # Make sure the link is absolute
                link = response.urljoin(link)
                
                # Pass title and link to parse_single using meta
                yield scrapy.Request(
                    link,
                    callback=self.parse_single,
                    meta={'title': title, 'link': link}
                )
        for next_page in response.css('a._95dd93c1'):
            yield response.follow(next_page, self.parse)
            
    def parse_single(self, response):
        title = response.meta['title']
        link = response.meta['link']

        def extract_detail_by_aria_label(label_text):
            element = response.css(f'span[aria-label="{label_text}"]')
            return element.css("::text").get(default="").strip()

        def extract_detail_by_aria_label_image(label_text):
            element = response.css(f'img[aria-label="{label_text}"]')
            return element.css("::attr(src)").get(default="").strip()
        
        purpose = extract_detail_by_aria_label('Purpose')
        property_id = extract_detail_by_aria_label('Reference')
        types = extract_detail_by_aria_label('Type')
        added_on = extract_detail_by_aria_label('Reactivated date')
        furnishing = extract_detail_by_aria_label('Furnishing')
        price = extract_detail_by_aria_label('Price')


        location = ""
        location_text = response.css('div._2fcf6c67 div[aria-label="Property header"]::text').get()
        location = location_text.strip()


        
        permit_number = response.css('div._62f2ec05 div._948d9e0a._1cc8fb85._95d4067f ul._1deff3aa li span[aria-label="Permit Number"]::text').get(default="").strip()
        

        agent_name = ""
        agent_name_1 = response.css('div._948d9e0a.f5686b16._95d4067f span._64aa14db a[aria-label="Agent name"] h2::text').get()
        agent_name_2 = response.css('div._948d9e0a._2f598d31._95d4067f span._4c376836 a[aria-label="Agent name"] h2::text').get()
        agent_name = agent_name_1 or agent_name_2

        if agent_name:
            agent_name = agent_name.strip()
        


        primary_image_url = extract_detail_by_aria_label_image('Cover Photo')

        breadcrumb_items = response.css('div._3624d529 a::text').getall()  # Grabs text of breadcrumb links
        
        
        last_breadcrumb = response.css('div._3624d529 span._43ad44d9::text').get()

        breadcrumb_items.append(last_breadcrumb.strip())

        
        breadcrumb_text = ' > '.join([text.strip() for text in breadcrumb_items])


        #amenities = extract_detail_by_aria_label('')
        description = response.css('div[dir="auto"] span._3547dac9::text').getall()

        # Join the list of text parts into a single string (if there are multiple parts)
        if description:
            description = ' '.join(description).strip()
        # property_image_urls = extract_detail_by_aria_label('')
        image_urls = []
    
        # Extract JPEG and WebP image URLs
        for img in response.css('div._4cd64ac1 picture img'):
            image_url = img.css('::attr(src)').get()
            if image_url:
                image_urls.append(image_url)

        for source in response.css('div._4cd64ac1 picture source'):
            webp_url = source.css('::attr(srcset)').get()
            if webp_url:
                image_urls.append(webp_url)

        yield {
            'title': title,
            'link': link,
            'purpose': purpose,
            'property_id': property_id,
            'type' : types,
            'added_on' : added_on,
            'furnishing' : furnishing,
            'price' : price,
            'location' : location,
            'permit_number' : permit_number,
            'agent_name' : agent_name,
            'primary_image_url' : primary_image_url,
            'breadcrumbs' : breadcrumb_text,
            'description' : description,
            'property_image_urls':image_urls
            

        }