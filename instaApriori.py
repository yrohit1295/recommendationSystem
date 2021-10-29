from mrjob.job import MRJob
from mrjob.job import MRStep
from mrjob.util import log_to_stream, log_to_null
import re
import sys
import logging
from itertools import combinations

log = logging.getLogger(__name__)

WORD_RE = re.compile(r'[\w]+')


class InstaApriori(MRJob):
    """
    The class respresents the implemention of map reduce in MRJob, The class contains the functions for data
    cleaning and to find frequent items using Apriori algorithm
    """

    def set_up_logging(cls, quiet=False, verbose=True, stream=None):
        """
        Set up logging
        :param quiet: boolean default is False
        :param verbose: boolean defeault true
        :param stream: string
        :return: enable log for MRJpb
        """
        log_to_stream(name='mrjob', debug=verbose, stream=stream)
        log_to_stream(name='__main__', debug=verbose, stream=stream)

    frequent_items = []

    def configure_args(self):
        """
        Create configuration for MRJob. It contains the parameters that are passed from command line or
        we can say, It conatins command line argument passed for MRJob
        :return:
        """
        super(InstaApriori, self).configure_args()
        self.add_passthru_arg('-iteration', type=int, help="The current iteration. Not used as a command line argument")
        self.add_passthru_arg('--k', type=int, default=3, help="Specify the maximum size of itemsets to find")
        self.add_passthru_arg('--s', type=float, help="Specify the minimum support threshold")
        self.add_passthru_arg('--c', type=float, default=0, help="Specify the minimum confidence threshold")
        self.add_file_arg('--f', default='frequent.txt',
                          help="Specify the name of the file used to store frequent itemsets")

    def steps(self):
        """
        Setup multiple steps for MRJob
        The function contain the steps for data clean and Apriori algorithm. The first step is used to call mapper
        and reducer for data cleaning and second step is used to call mapper_init, mapper, combiner, and reducer
        to get frequent items
        :return:
        """
        return [
            MRStep(mapper=self.mapper_data_cleaning,
                   reducer=self.reducer_data_cleaning
                   ),
            MRStep(
                mapper_init=self.mapper_get_items_init,
                mapper=self.mapper_get_items,
                combiner=self.combiner_count_items,
                reducer=self.reducer_total_items
            )
        ]

    def mapper_data_cleaning(self, l, line):
        """
        The function used to clean the dateset but spliting each line of CSV and return useful data
        like member_number and description
        :param l: string
        :param line: string
        :return: dict
        """
        lineitems = line.split(",")
        yield (lineitems[0], lineitems[2])

    def reducer_data_cleaning(self, order_id, product_id_arr):
        """
        Arrage items of similar transactions or member_number
        :param order_id: string is member_number
        :param product_id_arr: list contains the items of particular member_number
        :return: dict
        """
        order_dict = {}
        product_list = list()
        for product_id in product_id_arr:
            product_list.append(str(product_id))
        if order_id != 'Member_number':
            order_dict[order_id] = product_list
            yield order_dict, 1

    def mapper_get_items_init(self):
        """
        Initialize or read frequent item list
        :return: dict
        """
        if int(self.options.iteration) > 1:
            with open(self.options.f, 'r') as fh:
                self.frequent_items = set(fh.read().splitlines())
        else:
            self.frequent_items = {}

    def mapper_get_items(self, key_dict, value):
        """
        The mapper is used to find get the list of item and pairs with count 1
        :param key_dict: dict
        :param value: None
        :return: dict
        """
        for k in key_dict:
            lineitems = key_dict[k]
            # lineitems=value.split(",")
            if int(self.options.iteration) == 1:
                self.increment_counter("association_rules", 'transaction_count', 1)
                for item in lineitems:
                    yield item, 1
            else:
                itemsets = combinations(lineitems, self.options.iteration)
                frequent_itemsets = filter(lambda x: set(x) not in self.frequent_items, itemsets)
                for itemset in frequent_itemsets:
                    yield itemset, 1

    def combiner_count_items(self, item, counts):
        yield item, sum(counts)

    def reducer_total_items(self, item, counts):
        yield item, sum(counts)


if __name__ == '__main__':
    InstaApriori.run()
