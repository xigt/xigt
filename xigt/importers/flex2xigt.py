import xml.etree.ElementTree
import xigt
import re
from xigt.codecs import xigtxml
from print_xigt import printXigt

#TODO: fix punctuation as word problem
#TODO: Empty text in source file


def flex2xigt(flex_file):
    """
    Convert a flextext file to a XigtCorpus object
    :param flex_file: path to a flextext file
    :return: XigtCorpus object
    """
    igts = xigt.XigtCorpus()
    e = xml.etree.ElementTree.parse(flex_file)
    for igt in e.findall('interlinear-text'):
        L = ''
        L2 = ''
        G = ''
        G2 = ''
        T = ''

        g_ind = 0
        g_ind2 = 0
        new_igt = xigt.Igt()
        raw_tier = xigt.Tier(type='odin', id='r')
        norm_tier = xigt.Tier(type='odin', id='n')
        phrase_tier = xigt.Tier(type='phrases', id='p', segmentation='n')
        trans_tier = xigt.Tier(type='translations', id='t', alignment='p', content='n')
        phrase_ind = 0
        temp_phrase_ind = 0
        phrase_count = 0
        gloss_ind = 0
        trans_ind = 0
        for paragraph in igt.find('paragraphs').findall('paragraph'):
            if paragraph.find('phrases'):
                for phrase in paragraph.find('phrases').findall('phrase'):
                    phrase_count += 1

                    # possible segmentation="p1" etc
                    word_tier = xigt.Tier(type='words', id='w' + str(phrase_count), segmentation='p')
                    morph_tier = xigt.Tier(type='morphemes', id='m' + str(phrase_count), segmentation='w' + str(phrase_count))
                    gloss_tier = xigt.Tier(type='glosses', id='g' + str(phrase_count), alignment='m' + str(phrase_count), content='n')
                    word_ind = 0
                    temp_word_ind = 0
                    word_count = 0
                    for word in phrase.find('words').findall('word'):
                        morph_ind = 0
                        morph_ind2 = 0
                        morph_count = 0
                        word_count += 1

                        # if morphological segmentation present
                        if word.find('morphemes'):
                            for morph in word.find('morphemes').findall('morph'):
                                morph_count += 1

                                # Morph has no gloss, may be name
                                if len(morph) == 1:
                                    item = morph[0]
                                    if item.text:
                                        L2 += item.text
                                        morph_seg = 'w' + str(word_count) + '[' + str(morph_ind2) + ':' + str(
                                            morph_ind2 + len(item.text)) + ']'
                                        morph_ind2 += len(item.text)
                                        morph_item = xigt.Item(id='m' + str(word_count) + '.' + str(morph_count),
                                                               segmentation=morph_seg)
                                        morph_tier.append(morph_item)
                                        G2 += item.text
                                        gloss_seg = 'n2[' + str(gloss_ind) + ':' + str(gloss_ind + len(item.text)) + ']'
                                        gloss_ind += len(item.text)
                                        gloss_item = xigt.Item(id='g' + str(word_count) + '.' + str(morph_count),
                                                               content=gloss_seg,
                                                               alignment='m' + str(word_count) + '.' + str(morph_count))
                                        gloss_tier.append(gloss_item)
                                else:
                                    for item in morph:
                                        if item.get('type') == 'txt':
                                            L2 += item.text
                                            morph_seg = 'w' + str(word_count) + '[' + str(morph_ind2) + ':' + str(
                                                morph_ind2 + len(item.text)) + ']'
                                            morph_ind2 += len(item.text)
                                            morph_item = xigt.Item(id='m' + str(word_count) + '.' + str(morph_count),
                                                                  segmentation=morph_seg)
                                            morph_tier.append(morph_item)
                                        elif item.get('type') == 'gls':
                                            G2 += item.text
                                            gloss_seg = 'n2[' + str(gloss_ind) + ':' + str(gloss_ind + len(item.text)) + ']'
                                            gloss_ind += len(item.text)
                                            gloss_item = xigt.Item(id='g' + str(word_count) + '.' + str(morph_count),
                                                                  content=gloss_seg, alignment='m' + str(word_count) + '.' + str(morph_count))
                                            gloss_tier.append(gloss_item)
                            G2 += ' '
                            L2 += ' '
                            morph_ind2 += 1
                            gloss_ind += 1
                        for item in word.findall('item'):
                            if item.get('type') == 'punct':
                                L2 = L2.strip() + item.text + ' '
                                morph_ind2 += len(item.text)
                            else:
                                if item.get('type') == 'txt':
                                    L += item.text + ' '
                                    morph_ind += len(item.text) + 1
                                elif item.get('type') == 'gls':
                                    if item.text:
                                        G += item.text + ' '
                                    else:
                                        G += '[empty] '
                        temp_phrase_ind += morph_ind2
                        temp_word_ind += morph_ind2
                        word_seg = 'p' + str(phrase_count) + '[' + str(word_ind) + ':' + str(temp_word_ind - 1) + ']'
                        word_ind = temp_word_ind
                        word_item = xigt.Item(id='w' + str(word_count), segmentation=word_seg)
                        word_tier.append(word_item)
                    new_igt.append(word_tier)
                    new_igt.append(morph_tier)
                    new_igt.append(gloss_tier)
                    phrase_seg = 'n1[' + str(phrase_ind) + ':' + str(temp_phrase_ind) + ']'
                    phrase_ind = temp_phrase_ind
                    phrase_item = xigt.Item(id='p' + str(phrase_count), segmentation=phrase_seg)
                    phrase_tier.append(phrase_item)
                    for item in phrase.findall('item'):
                        if item.get('type') == "gls":
                            if item.text:
                                trans_item = xigt.Item(id='t' + str(phrase_count), alignment='p' + str(phrase_count),
                                                       content='n3[' + str(trans_ind) + ':' + str(trans_ind + len(item.text) - 1) + ']')
                                T += item.text + ' '
                                trans_ind += len(item.text) + 1
                                trans_tier.append(trans_item)
        l_item = xigt.Item(id='n1', text=L2)
        l_item.attributes['tag'] = 'L'
        raw_tier.append(l_item)
        norm_tier.append(l_item)
        g_item = xigt.Item(id='n2', text=G2)
        g_item.attributes['tag'] = 'G'
        raw_tier.append(g_item)
        norm_tier.append(g_item)
        t_item = xigt.Item(id='n3', text=T)
        t_item.attributes['tag'] = 'T'
        raw_tier.append(t_item)
        norm_tier.append(t_item)
        raw_tier.attributes['state'] = 'raw'
        new_igt.append(raw_tier)
        norm_tier.attributes['state'] = 'normalized'
        new_igt.append(norm_tier)
        new_igt.append(phrase_tier)
        new_igt.append(trans_tier)
        igts.append(new_igt)
    return igts

result = flex2xigt('nuuchahnulth2.flextext')
xigtxml.dump(open('test2.xml', 'w'), result)
print(printXigt(result))