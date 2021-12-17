import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn2_circles


def plot_venn(array_one, array_two, label_one, label_two):
    set1 = set(array_one)
    set2 = set(array_two)

    total = len(set1.difference(set2)) + len(set2.difference(set1)) + len(set1.intersection(set2))
    print(f"Total: {total}")

    plt.figure(figsize=(6,4))
    v = venn2(subsets = (len(set1.difference(set2)),
                         len(set2.difference(set1)),
                         len(set1.intersection(set2))), set_labels = (label_one, label_two))

    c = venn2_circles(subsets = (len(set1.difference(set2)),
                                 len(set2.difference(set1)),
                                 len(set1.intersection(set2))), linestyle='solid')

    plt.show()

    print(f"Precision: {round(len(set1.intersection(set2))/len(set2), 2)}")
    print(f"Recall: {round(len(set1.intersection(set2))/len(set1), 2)}")

def printmd(string):
    display(Markdown(string))
