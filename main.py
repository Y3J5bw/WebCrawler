from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import multiprocessing
import os


class Website:
    def __init__(self, link, ep_num):
        self.ep_num = ep_num
        self.link = link
        options = Options()
        [options.add_argument(arg) for arg in ["--disable-extensions", "--window-size=1920x1080"]]
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument('user-agent={0}'.format(user_agent))
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


class DramacoolDL(Website):
    def __init__(self, link, ep_num):
        Website.__init__(self, link, ep_num)

    def check_order(self):
        self.driver.get(f'{self.link}-episode-{self.ep_num}/')
        self.driver.find_element_by_xpath('//a[@href="' + '/download' + '"]').click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.find_element_by_xpath('//a[starts-with(@href, "https://dood.")]').click()
        self.driver.switch_to.window(self.driver.window_handles[2])
        return f'{self.ep_num}) {self.driver.find_element_by_class_name("size").text}'

    def temp(self):
        self.driver.get(f'{self.link}-episode-{self.ep_num}.html')
        return self.driver.find_element_by_class_name("doodstream").get_attribute("data-video")

    def grab(self):
        print(f'Extracting Download Link For: {self.link} Ep: {self.ep_num}')
        self.driver.get(f'{self.link}-episode-{self.ep_num}')
        # try:
            # self.driver.find_element_by_xpath('//a[@href="'+'/download'+'"]').click()
            # self.driver.find_element_by_xpath('//a[starts-with(@href, "//asianembed.io/download")]').click()
            # WebDriverWait(self.driver, 1000).until(EC.element_to_be_clickable(
            #     (By.XPATH, '//a[starts-with(@href, "//asianembed.io/download")]'))).click()
        self.driver.switch_to.frame(self.driver.find_element_by_tag_name("iframe"))
        temp_link = WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(self.driver.find_element_by_xpath("//iframe[starts-with(@src, 'https://')]"))).get_attribute("data-server")
        print(temp_link)
        self.driver.get(f'https://asianembed.io/download?{temp_link[36:]}&mip=0.0.0.0')
        '''
        except NoSuchElementException:
            try:
                print('safsefsefsefsefsefsefsef')
                WebDriverWait(self.driver, 1000).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[starts-with(@href, "//asianembed.io/download")]'))).click()

            except Exception:
                print('Could not find download button')
                return f'Error: {self.link} Ep: {self.ep_num}'
        '''

        self.driver.switch_to.window(self.driver.window_handles[1])
        try:
            link = self.driver.find_element_by_xpath('//a[starts-with(@href, "https://dood.")]')\
                .get_attribute("href")

        except NoSuchElementException:
            print('Could not find Doodstream download link')
            try:
                link = self.driver.find_element_by_xpath('//a[starts-with(@href, "https://mp4upload.com")]') \
                    .get_attribute("href")

            except NoSuchElementException:
                print('Could not find mp4upload download link')
                try:
                    link = self.driver.find_element_by_xpath('//a[starts-with(@href, "https://streamsb")]') \
                        .get_attribute("href")

                except NoSuchElementException:
                    print('Could not find xstreamcdn download link')
                    try:
                        link = self.driver.find_element_by_xpath('//a[starts-with(@href, "https://fcdn.stream")]') \
                            .get_attribute("href")
                        
                    except NoSuchElementException:
                        print('Could not find xstreamcdn mirror download link')
                        link = f'Error: {self.link} Ep: {self.ep_num}'

        return link


class FdramaDL(Website):
    def __init__(self, link, ep_num):
        Website.__init__(self, link, ep_num)

    def grab(self):
        print(f'Extracting Download Link For: {self.link} Ep: {self.ep_num}')
        self.driver.get(self.link)
        try:
            self.driver.find_element_by_xpath(f'//a[starts-with(@href, "https://player.fastdrama.org/embed/dl/") '
                                              f'and contains(@title, '
                                              f'{str(self.ep_num) if len(str(self.ep_num)) != 1 else "0" + str(self.ep_num)}'
                                              f')]').click()

        except NoSuchElementException:
            print('Could not find Download Link')
            return f'Error: {self.link} Ep: {self.ep_num}'

        self.driver.switch_to.window(self.driver.window_handles[1])
        try:
            self.driver.find_element_by_xpath(
                '//a[starts-with(@href, "http://player.fastdrama.org/embed/dl/link") and '
                'contains(@title, "MP")]').click()

        except NoSuchElementException:
            try:
                self.driver.find_element_by_xpath(
                    '//a[starts-with(@href, "http://player.fastdrama.org/embed/dl/link") and '
                    'contains(@title, "MD")]').click()

            except NoSuchElementException:
                try:
                    self.driver.find_element_by_xpath(
                        '//a[starts-with(@href, "http://player.fastdrama.org/embed/dl/link") and '
                        'contains(@title, "UT")]').click()

                except NoSuchElementException:
                    print('Could not find download link')
                    return f'Error: {self.link} Ep: {self.ep_num}'

        self.driver.switch_to.window(self.driver.window_handles[2])
        return self.driver.current_url


shows = {"https://www.dramacool9.co/sweet-combat": 37}

total_errors = []


def worker(show):
    links = []
    errors = []
    with multiprocessing.Pool(processes=8) as pool:
        links.extend(pool.map(subworker, [[show, i] for i in range(1, shows[show] + 1)]))
    for link in links:
        if link[:5] == "Error":
            errors.append(link)
            links.remove(link)
    return links, errors


def subworker(data):
    instance = DramacoolDL(data[0], data[1])
    link = instance.grab()
    instance.driver.quit()
    return link


def size_worker():
    sizes = []
    with multiprocessing.Pool(processes=16) as pool:
        for show in shows:
            sizes.extend([pool.map(get_size_worker, [[show, i, sizes] for i in range(1, shows[show] + 1)])])

    return sorted(sizes[0], key=lambda x: int(x.partition(')')[0]))


def get_size_worker(data):
    instance = DramacoolDL(data[0], data[1])
    size = instance.check_order()
    instance.driver.quit()
    return size


def copy_link(lists):
    print(lists[0])
    os.system('echo | set /p nul=' + ' '.join(lists[0]) + '| clip')
    print('\n'.join(lists[1]) if lists[1] else "No Errors")
    print(f'Starting Download for {len(lists[0])} Eps')
    total_errors.append(lists[1])


if __name__ == '__main__':
    os.environ['WDM_LOG_LEVEL'] = '0'
    for show in shows:
        copy_link(worker(show))

    quit()
