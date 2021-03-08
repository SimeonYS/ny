import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NyItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class NySpider(scrapy.Spider):
	name = 'ny'
	start_urls = ['https://www.nykredit.com/presse-og-nyheder/nyheder/']

	def parse(self, response):
		articles = response.xpath('//div[@class="section"]')
		for article in articles:
			date = article.xpath('.//h4/text()').get()
			date = re.findall(r'\d+\.\s\w+\s\d+',date)
			post_links = article.xpath('.//a/@href').getall()
			yield from response.follow_all(post_links, self.parse_post,cb_kwargs=dict(date=date))

	def parse_post(self, response,date):

		title = response.xpath('//h1/text()').get()
		content = response.xpath('//p[@class="mdc-typography--subtitle preserve-linebreaks"]//text()').getall() + response.xpath('//div[@class="section section--text-image theme--white"]//text()').getall()
		if not content:
			content = response.xpath('//p[@class="article__lead mdc-typography--subtitle-lg"]//text()').getall() + response.xpath('//div[@class="mdc-layout-grid"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NyItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
