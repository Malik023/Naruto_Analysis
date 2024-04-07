import scrapy

class BlogSpider(scrapy.Spider):
    name = 'narutospider'
    start_urls = ['https://naruto.fandom.com/wiki/Special:BrowseData/Jutsu?limit=250&offset=0&_cat=Jutsu']

    def parse(self, response):
        for href in response.css('.smw-columnlist-container a::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href), callback=self.parse_jutsu)

        for next_page in response.css('a.mw-nextlink'):
            yield response.follow(next_page, self.parse)

    def parse_jutsu(self, response):
        jutsu_name = response.xpath('//h1[@class="page-header__title"]/text()').get()



        if jutsu_name:
            jutsu_name = jutsu_name.strip()
        else:
            self.logger.warning('Failed to extract jutsu name from URL: %s', response.url)
            return

        jutsu_type = ""
        jutsu_description = ""
        aside = response.css('aside')
        if aside:
            for cell in aside.css('.pi-data'):
                cell_name = cell.css('h3::text').get().strip()
                if cell_name == 'Classification':
                    jutsu_type = cell.css('div::text').get().strip()

        description_paragraphs = response.css('.mw-parser-output p')
        if description_paragraphs:
            jutsu_description = ' '.join(p.get() for p in description_paragraphs).strip()

        yield {
            'jutsu_name': jutsu_name,
            'jutsu_type': jutsu_type,
            'jutsu_description': jutsu_description
        }
