Modifications to xigt/importers/toolbox.py as of 18 DEC 2018
Corbett Moore (UW CLMS)

	* Method make_tier() has been modified to include segmentation for tier_types 'words'
		and 'morphemes.' (lines 251-293). There are three options for writing the Item
		data to the output:
		* When there is a valid segment (lines 267-273), write with segmentation.
		* Imprecise segment found (lines 274-279), write with segmentation. If a comment
			is desired to alert human operators to imprecise segmentation, add the code here.
		* No segmentation desired (lines 281-285), eg for tier_type 'gloss'
	* New method align_word() has been added to provide segmentation data for the make_tier()
		method. Segmentation rules for morphemes are as follows:
			* When there is one morpheme, it segments to the full word without attempting to
				match characters (eg, 'cat' segments to 'cat' as [0:3])
			* Target token is reduced to lower case. NOTE this may cause problems with
				Unicode characters (á â ß ë ø, et al)
			* First morpheme in the sequence can be compared directly to first N characters
				of the token and returns if the characters match exactly (eg, 'broom'
				segments to 'brooms' as [0:5]). If there is no match, return an ambiguous
				segmentation (see below).
			* For morphemes after the first:
				* Build an amalgam of the previous morphemes, including, where appropriate,
					hyphens found in the original orthography (eg, finding 'lantern' in
					"jack-o'-lantern" first builds "jack-o'-")
				* Try matching the first N characters (the length of the amalgam) to the
					target token. If there is a match, we can attempt to segment the
					target morpheme. If not, return the entire remainder of the word as
					an ambiguous segment for that morpheme (eg, 'horror' + '-ify' both
					segment to 'horrify' as [0:7], because 'horror' does not match; thus
					all morphemes after the first failure will also fail)
				* Last morpheme in the sequence (2nd of 2, 3rd of 3) is segmented to the
					remainder of the word even if it does not match (eg, '-s' segments
					to 'witches' as [5:7])
			* If no match is found (eg, the amalgam fails), return the remainder of the
				word as ambiguous.
			* Inter-tag text has been left intact (eg, <item id='w1' ...>cat</item>) for
				non-lossy conversion (no data is lost).
		
		align_word() takes the following arguments:
			* tier_type: eg, 'words', 'morphemes'
			* integer: the index of the token we are currently working on
			* src_data: tuple as follows:
				* for 'words': ('SOME VARIOUS STRINGS.', ['SOME', 'VARIOUS', 'STRINGS.'])
				* for 'morphemes': ('STRING', ['ST-', 'RI', '-NG']), boundary placement
					can vary
		align_word() returns the following:
			* beg: index of the beginning of the segment, or -1 (boundary not found)
			* end: index of the end of the segment, or -1 (boundary not found)
			* cmt: 0 (segment found) or -1 (imprecise segmentation)
		
		
	* Default morpheme boundaries [-, =, ., ~] added in variable default_bounds (line 107)
	
