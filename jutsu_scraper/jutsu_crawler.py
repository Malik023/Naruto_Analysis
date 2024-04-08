import scrapy
from bs4 import BeautifulSoup

class BlogSpider(scrapy.Spider):
    # Name of the spider
    name = 'narutospider'
    
    # Starting URL for the spider
    start_urls = ['https://naruto.fandom.com/wiki/Special:BrowseData/Jutsu?limit=250&offset=0&_cat=Jutsu']

    # Function to parse the response from the start URL
    def parse(self, response):
        # Extracting all the links for individual jutsu from the main page
        for href in response.css('div.smw-columnlist-container')[0].css('a::attr(href)').extract():
            # Sending request to each jutsu page and calling parse_jutsu method for further parsing
            extracted_data = scrapy.Request("https://naruto.fandom.com"+href, callback=self.parse_jutsu)
            yield extracted_data

        # Following pagination links to navigate to next pages if they exist
        for next_page in response.css('a.mw-nextlink'):
            yield response.follow(next_page, self.parse)
    
    # Function to parse individual jutsu pages
    def parse_jutsu(self, response):
        # Extracting the name of the jutsu
        jutsu_name = response.css('h1.page-header__title::text').extract()[0].strip()

        # Extracting HTML content of the main div
        div_selector = response.css('div.mw-parser-output')[0]
        div_html = div_selector.extract()

        # Using BeautifulSoup to manipulate the HTML content
        soup = BeautifulSoup(div_html).find('div')

        # Removing unwanted elements from the soup
        if soup.find('div', {'id': 'quiz_module_desktop_placement_styles'}):
            soup.find('div', {'id': 'quiz_module_desktop_placement_styles'}).decompose()
        
        if soup.find('h2', {'id': 'quiz_module_destkop_header_styles'}):
            soup.find('h2', {'id': 'quiz_module_destkop_header_styles'}).decompose()
        
        if soup.find('a', {'id': 'quiz_module_desktop_link_styles'}):
            soup.find('a', {'id': 'quiz_module_desktop_link_styles'}).decompose()

        # Initializing jutsu type
        jutsu_type = ""
        
        # Extracting jutsu type from aside section if it exists
        if soup.find('aside'):
            aside = soup.find('aside')
            for cell in aside.find_all('div', {'class': 'pi-data'}):
                if cell.find('h3'):
                    cell_name = cell.find('h3').text.strip()
                    if cell_name == 'Classification':
                        jutsu_type = cell.find('div').text.strip()

            # Removing aside section from the soup
            soup.find('aside').decompose()

        # Extracting jutsu description from the modified soup
        jutsu_description = soup.text
        jutsu_description = jutsu_description.split('Trivia')[0].strip()

        # Yielding the extracted jutsu information as a dictionary
        yield dict(   
                    jutsu_name = jutsu_name,
                    jutsu_type = jutsu_type,
                    jutsu_description = jutsu_description

                )
