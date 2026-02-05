import re
import random
from typing import Dict, List, Optional, Tuple
from ..utils.config import Config
from ..utils.error_handling import ContentGenerationError, log_function_call
import logging

logger = logging.getLogger(__name__)

class SatireEngine:
    """
    Core engine for transforming real news into deadpan satire.
    """
    
    def __init__(self):
        self.satire_patterns = self._load_satire_patterns()
        self.expert_names = self._generate_expert_names()
        self.corporate_speak = self._load_corporate_speak()
        self.political_speak = self._load_political_speak()
    
    @log_function_call
    def transform_article(self, news_article: Dict) -> Dict:
        """
        Transform a real news article into deadpan satire.
        
        Args:
            news_article: Original news article from NewsData.io
            
        Returns:
            Transformed satire article with metadata
        """
        try:
            # Extract key information
            title = news_article.get('title', '')
            content = news_article.get('content', '') or news_article.get('description', '')
            category = news_article.get('category', '')
            
            # Analyze for satirical potential
            satire_score = self._calculate_satire_potential(news_article)
            if satire_score < Config.SATIRE_THRESHOLD:
                raise ContentGenerationError(f"Article satire score {satire_score} below threshold {Config.SATIRE_THRESHOLD}")
            
            # Generate satirical headline
            satirical_headline = self._generate_headline(title, category)
            
            # Generate opening paragraph
            opening_paragraph = self._generate_opening_paragraph(title, content, category)
            
            # Generate body paragraphs
            body_paragraphs = self._generate_body_paragraphs(content, category)
            
            # Generate expert quotes
            expert_quotes = self._generate_expert_quotes(category)
            
            # Assemble the full article
            satire_article = {
                'headline': satirical_headline,
                'opening_paragraph': opening_paragraph,
                'body_paragraphs': body_paragraphs,
                'expert_quotes': expert_quotes,
                'category': category,
                'original_article': news_article,
                'satire_score': satire_score,
                'byline': self._generate_byline(),
                'timestamp': self._generate_timestamp()
            }
            
            logger.info(f"Successfully transformed article: '{satirical_headline[:50]}...'")
            return satire_article
            
        except Exception as e:
            logger.error(f"Failed to transform article: {str(e)}")
            raise ContentGenerationError(f"Article transformation failed: {str(e)}")
    
    def _calculate_satire_potential(self, article: Dict) -> float:
        """
        Calculate the satirical potential of an article (0-10 scale).
        
        Higher scores indicate better satirical potential.
        """
        score = 0.0
        title = article.get('title', '').lower()
        content = (article.get('content', '') or article.get('description', '')).lower()
        category = article.get('category', '').lower()
        
        # Hypocrisy indicators
        hypocrisy_keywords = [
            'announces', 'claims', 'insists', 'maintains', 'declares',
            'contradicts', 'reverses', 'flip-flops', 'backtracks'
        ]
        hypocrisy_score = sum(1 for keyword in hypocrisy_keywords if keyword in title or content)
        score += hypocrisy_score * 1.5
        
        # Corporate/government speak
        corporate_keywords = [
            'synergy', 'paradigm', 'leverage', 'optimize', 'streamline',
            'restructuring', 'rightsizing', 'efficiency', 'productivity'
        ]
        corporate_score = sum(1 for keyword in corporate_keywords if keyword in content)
        score += corporate_score * 1.2
        
        # Political doublespeak
        political_keywords = [
            'fiscal responsibility', 'government waste', 'taxpayer money',
            'national security', 'public interest', 'bipartisan'
        ]
        political_score = sum(1 for keyword in political_keywords if keyword in content)
        score += political_score * 1.3
        
        # Contradiction detection
        contradiction_patterns = [
            r'cuts.*while.*increasing',
            r'reduces.*but.*expands',
            r'saves.*by.*spending',
            r'protects.*by.*limiting'
        ]
        contradiction_score = sum(1 for pattern in contradiction_patterns if re.search(pattern, content))
        score += contradiction_score * 2.0
        
        # Category bonus
        high_satire_categories = ['politics', 'business', 'technology']
        if category in high_satire_categories:
            score += 1.0
        
        # Length and substance bonus
        if len(content) > 200:
            score += 0.5
        
        return min(score, 10.0)
    
    def _generate_headline(self, original_title: str, category: str) -> str:
        """
        Generate a deadpan satirical headline.
        """
        # Extract key entities and actions
        words = original_title.split()
        
        # Common satirical patterns
        patterns = [
            "{entity} Discovers {contradiction}",
            "{entity} Announces {ironic_action}",
            "{entity} Reveals {hypocrisy}",
            "Study Finds {obvious_truth}",
            "{entity} Achieves {ironic_accomplishment}"
        ]
        
        # Extract entities (simplified)
        entities = self._extract_entities(original_title)
        if not entities:
            entities = ["Officials", "Company", "Organization"]
        
        # Generate contradictions based on category
        contradictions = {
            'politics': [
                "Government Waste Only Exists In Programs That Help People",
                "Fiscal Responsibility Applies Selectively To Non-Defense Spending",
                "Bipartisanship Means Everyone Agrees With My Position"
            ],
            'business': [
                "Company Cannot Afford The People Who Made It Valuable",
                "Innovation Requires Eliminating The Innovators",
                "Efficiency Means Working Harder For Less Money"
            ],
            'technology': [
                "Tech CEO Discovers Real Communication Requires Physical Presence",
                "Social Media Platform Announces Plans To Reduce Social Interaction",
                "AI Company Replaces Creative Team With Algorithm"
            ]
        }
        
        category_contradictions = contradictions.get(category, [
            "Organization Achieves Ironic Outcome",
            "Entity Discovers Contradictory Truth"
        ])
        
        # Select or generate headline
        if random.random() < 0.3 and entities:
            # Use pattern-based generation
            pattern = random.choice(patterns)
            entity = random.choice(entities)
            contradiction = random.choice(category_contradictions)
            
            headline = pattern.format(
                entity=entity,
                contradiction=contradiction,
                ironic_action=self._generate_ironic_action(category),
                hypocrisy=self._generate_hypocrisy(category),
                obvious_truth=self._generate_obvious_truth(category),
                ironic_accomplishment=self._generate_ironic_accomplishment(category)
            )
        else:
            # Use transformation-based approach
            headline = self._transform_headline(original_title, category)
        
        # Ensure proper length
        while len(headline.split()) < Config.HEADLINE_MIN_WORDS:
            headline += " " + random.choice(["Report Finds", "Study Shows", "Officials Say"])
        
        while len(headline.split()) > Config.HEADLINE_MAX_WORDS:
            headline = ' '.join(headline.split()[:Config.HEADLINE_MAX_WORDS])
        
        return headline
    
    def _transform_headline(self, original: str, category: str) -> str:
        """
        Transform an original headline into satirical form.
        """
        # Common transformations
        transformations = {
            r'announces.*new': 'Discovers',
            r'claims.*will': 'Insists Will',
            r'reports.*increase': 'Celebrates Increase In',
            r'warns.*about': 'Expresses Concern About',
            r'cuts.*funding': 'Optimizes Funding By Eliminating',
            r'expands.*program': 'Streamlines Program By Expanding'
        }
        
        transformed = original
        for pattern, replacement in transformations.items():
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
        
        # Add ironic qualifiers
        if category == 'politics' and 'spending' in transformed.lower():
            transformed += " For The People"
        elif category == 'business' and 'layoffs' in transformed.lower():
            transformed += " To Enhance Shareholder Value"
        
        return transformed
    
    def _generate_opening_paragraph(self, title: str, content: str, category: str) -> str:
        """
        Generate the opening paragraph (2-3 sentences).
        """
        # Extract key information
        main_entity = self._extract_main_entity(title)
        key_action = self._extract_key_action(title)
        
        # Generate sentences based on category patterns
        if category == 'politics':
            sentences = [
                f"After years of {self._get_political_experience()} on the issue, {main_entity} announced today that {key_action} represents a fundamental shift in how government {self._get_government_function()}.",
                f"The decision, made during a {self._get_political_setting()}, comes as polls show overwhelming public support for the exact opposite approach.",
                f"'This is about {self._get_political_value()},' {main_entity} explained while {self._get_ironic_action()}."
            ]
        elif category == 'business':
            sentences = [
                f"Just {self._get_timeframe()} after {self._get_business_achievement()}, {main_entity} announced today that {key_action} is essential for {self._get_business_goal()}.",
                f"The move, described internally as '{self._get_corporate_buzzword()}', will affect {self._get_affected_people()} who {self._get_employee_contribution()}.",
                f"'We remain committed to {self._get_corporate_value()},' stated {main_entity} in a {self._get_communication_method()}."
            ]
        else:  # technology or general
            sentences = [
                f"In a stunning development that {self._get_tech_impact()}, {main_entity} revealed today that {key_action} represents the future of {self._get_tech_field()}.",
                f"The announcement, made via {self._get_tech_platform()}, demonstrates how {self._get_tech_concept()} is {self._get_tech_transformation()}.",
                f"Experts suggest this could {self._get_tech_consequence()} while {self._get_tech_side_effect()}."
            ]
        
        # Select 2-3 sentences
        num_sentences = random.randint(2, 3)
        selected_sentences = random.sample(sentences, min(num_sentences, len(sentences)))
        
        return ' '.join(selected_sentences)
    
    def _generate_body_paragraphs(self, content: str, category: str) -> List[str]:
        """
        Generate 3-5 body paragraphs.
        """
        paragraphs = []
        
        # Paragraph 1: Context and background
        context_paragraph = self._generate_context_paragraph(content, category)
        paragraphs.append(context_paragraph)
        
        # Paragraph 2: Details and implications
        details_paragraph = self._generate_details_paragraph(content, category)
        paragraphs.append(details_paragraph)
        
        # Paragraph 3: Expert perspective
        expert_paragraph = self._generate_expert_perspective(category)
        paragraphs.append(expert_paragraph)
        
        # Paragraph 4: Future outlook (optional)
        if random.random() < 0.7:
            outlook_paragraph = self._generate_outlook_paragraph(category)
            paragraphs.append(outlook_paragraph)
        
        # Paragraph 5: Historical context (optional)
        if random.random() < 0.5:
            history_paragraph = self._generate_history_paragraph(category)
            paragraphs.append(history_paragraph)
        
        return paragraphs[:Config.BODY_MAX_PARAGRAPHS]
    
    def _generate_expert_quotes(self, category: str) -> List[Dict]:
        """
        Generate 1-2 fictional expert quotes.
        """
        quotes = []
        
        # Generate 1-2 quotes
        num_quotes = random.randint(1, 2)
        
        for i in range(num_quotes):
            expert = self._generate_expert(category)
            quote = self._generate_quote(category, i)
            
            quotes.append({
                'expert': expert,
                'quote': quote,
                'affiliation': self._generate_affiliation(category)
            })
        
        return quotes
    
    def _extract_entities(self, text: str) -> List[str]:
        """
        Extract potential entities from text (simplified).
        """
        # This is a simplified version - in production, you'd use NLP
        words = text.split()
        entities = []
        
        # Look for capitalized words (potential entities)
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3:
                # Check if it's not at the beginning of the sentence
                if i > 0 and words[i-1][-1] != '.':
                    entities.append(word)
        
        return list(set(entities))[:5]  # Return up to 5 unique entities
    
    def _extract_main_entity(self, title: str) -> str:
        """
        Extract the main entity from a title.
        """
        entities = self._extract_entities(title)
        if entities:
            return entities[0]
        return "Officials"
    
    def _extract_key_action(self, title: str) -> str:
        """
        Extract the key action from a title.
        """
        # Look for action words
        action_words = ['announces', 'claims', 'reports', 'warns', 'cuts', 'expands', 'launches', 'reveals']
        
        for word in action_words:
            if word in title.lower():
                return word
        
        return "action"
    
    # Helper methods for generating content
    def _generate_ironic_action(self, category: str) -> str:
        actions = {
            'politics': 'accepting campaign contributions from affected industries',
            'business': 'laying off the innovation team',
            'technology': 'using a flip phone for the announcement'
        }
        return actions.get(category, 'performing the exact opposite action')
    
    def _generate_hypocrisy(self, category: str) -> str:
        hypocrisies = {
            'politics': 'Principles Apply Only To Opponents',
            'business': 'Efficiency Means Fewer Jobs',
            'technology': 'Innovation Requires Eliminating Innovation'
        }
        return hypocrisies.get(category, 'Contradictory Behavior')
    
    def _generate_obvious_truth(self, category: str) -> str:
        truths = {
            'politics': 'Politicians Want To Be Re-elected',
            'business': 'Companies Want To Make Money',
            'technology': 'Technology Changes Things'
        }
        return truths.get(category, 'Self-Evident Reality')
    
    def _generate_ironic_accomplishment(self, category: str) -> str:
        accomplishments = {
            'politics': 'Solving Problem They Created',
            'business': 'Maximizing Shareholder Value Through Employee Elimination',
            'technology': 'Revolutionizing Industry By Making It Worse'
        }
        return accomplishments.get(category, 'Ironic Achievement')
    
    def _get_political_experience(self) -> str:
        return random.choice(['ignoring', 'exploiting', 'profiting from', 'denying'])
    
    def _get_government_function(self) -> str:
        return random.choice(['serves its citizens', 'wastes taxpayer money', 'protects democracy', 'regulates industry'])
    
    def _get_political_setting(self) -> str:
        return random.choice(['a press conference', 'a closed-door meeting', 'a campaign rally', 'an interview'])
    
    def _get_political_value(self) -> str:
        return random.choice(['fiscal responsibility', 'protecting American families', 'national security', 'the American dream'])
    
    def _get_timeframe(self) -> str:
        return random.choice(['three months', 'six months', 'one year', 'two years'])
    
    def _get_business_achievement(self) -> str:
        return random.choice(['record profits', 'successful fundraising', 'market expansion', 'product launch'])
    
    def _get_business_goal(self) -> str:
        return random.choice(['long-term growth', 'operational efficiency', 'market competitiveness', 'shareholder value'])
    
    def _get_corporate_buzzword(self() -> str:
        return random.choice(['synergistic realignment', 'paradigm shift', 'operational optimization', 'strategic restructuring'])
    
    def _get_affected_people(self) -> str:
        return random.choice(['employees', 'workers', 'team members', 'staff'])
    
    def _get_employee_contribution(self) -> str:
        return random.choice(['built the company', 'achieved record productivity', 'made the company valuable', 'drove innovation'])
    
    def _get_corporate_value(self) -> str:
        return random.choice(['our people', 'innovation', 'excellence', 'sustainability'])
    
    def _get_communication_method(self) -> str:
        return random.choice(['company-wide email', 'press release', 'all-hands meeting', 'internal memo'])
    
    def _get_tech_impact(self) -> str:
        return random.choice(['will change everything', 'revolutionizes the industry', 'disrupts the status quo', 'transforms how we live'])
    
    def _get_tech_field(self) -> str:
        return random.choice(['communication', 'work', 'social interaction', 'human connection'])
    
    def _get_tech_platform(self() -> str:
        return random.choice(['Twitter', 'LinkedIn', 'company blog', 'tech conference'])
    
    def _get_tech_concept(self) -> str:
        return random.choice(['artificial intelligence', 'machine learning', 'blockchain', 'the metaverse'])
    
    def _get_tech_transformation(self) -> str:
        return random.choice(['making human connection obsolete', 'eliminating the need for physical presence', 'optimizing social interaction', 'revolutionizing communication'])
    
    def _get_tech_consequence(self) -> str:
        return random.choice(['increase productivity', 'streamline operations', 'enhance user experience', 'drive growth'])
    
    def _get_tech_side_effect(self) -> str:
        return random.choice(['eliminating jobs', 'reducing human interaction', 'increasing surveillance', 'concentrating power'])
    
    def _generate_context_paragraph(self, content: str, category: str) -> str:
        """Generate the first body paragraph with context."""
        if category == 'politics':
            return f"The announcement comes at a critical time when {random.choice(['public trust in institutions is at an all-time low', 'the nation faces unprecedented challenges', 'voters are demanding real change'])}. According to {random.choice(['recent polls', 'expert analysis', 'insider reports'])}, {random.choice(['the majority of Americans', 'key stakeholders', 'industry leaders'])} have been {random.choice(['calling for action', 'expressing concern', 'demanding accountability'])} on this issue for months."
        elif category == 'business':
            return f"The decision reflects broader trends in the industry, where companies are increasingly {random.choice(['prioritizing shareholder value', 'embracing digital transformation', 'optimizing operations'])}. Market analysts note that this move could {random.choice(['set a precedent', 'trigger similar actions', 'reshape the competitive landscape'])} as other firms face {random.choice(['similar pressures', 'comparable challenges', 'identical market conditions'])}."
        else:
            return f"This development highlights the ongoing tension between {random.choice(['innovation and tradition', 'progress and privacy', 'efficiency and humanity'])} in the technology sector. Industry observers suggest that such announcements have become {random.choice(['increasingly common', 'remarkably frequent', 'notably predictable'])} as companies grapple with {random.choice(['rapid technological change', 'evolving consumer expectations', 'intensifying competition'])}."
    
    def _generate_details_paragraph(self, content: str, category: str) -> str:
        """Generate the second body paragraph with details."""
        if category == 'politics':
            return f"Implementation details remain {random.choice(['unclear', 'vague', 'subject to further clarification'])}, though sources close to the {random.choice(['administration', 'legislation', 'initiative'])} suggest that {random.choice(['significant resources', 'substantial funding', 'considerable political capital'])} will be required. Critics have already pointed out that the proposal {random.choice(['lacks specific metrics', 'contains numerous loopholes', 'fails to address root causes'])}, while supporters argue that {random.choice(['bold action is necessary', 'the time for debate is over', 'this represents real progress'])}."
        elif category == 'business':
            return f"Financial implications of the move are expected to be {random.choice(['significant', 'substantial', 'notable'])}, with analysts projecting {random.choice(['cost savings', 'efficiency gains', 'productivity improvements'])} of approximately {random.choice(['$10-15 million', '15-20%', 'a significant amount'])} over the next fiscal year. However, questions remain about {random.choice(['long-term sustainability', 'employee morale', 'customer impact'])}, particularly given the company's recent {random.choice(['performance', 'strategic direction', 'market position'])}."
        else:
            return f"Technical specifications released by the company indicate that the new {random.choice(['platform', 'system', 'technology'])} will {random.choice(['leverage cutting-edge algorithms', 'utilize advanced machine learning', 'employ sophisticated architecture'])} to deliver {random.choice(['unprecedented performance', 'revolutionary capabilities', 'transformative experiences'])}. Early testers report that while the system {random.choice(['shows promise', 'demonstrates potential', 'offers improvements'])}, there are concerns about {random.choice(['scalability', 'privacy implications', 'user adoption'])}."
    
    def _generate_expert_perspective(self, category: str) -> str:
        """Generate a paragraph with expert perspective."""
        expert_name = random.choice(self.expert_names)
        expertise = self._get_expertise(category)
        
        return f"\"This is {random.choice(['a classic example of', 'typical for', 'characteristic of'])} how {random.choice(['power structures', 'institutional dynamics', 'organizational behavior'])} operate in the {category} sector,\" explains {expert_name}, {expertise} at {random.choice(['a leading think tank', 'a prestigious university', 'an independent research institute'])}. \"What we're seeing is {random.choice(['the predictable outcome', 'a natural consequence', 'an inevitable result'])} of {random.choice(['systemic incentives', 'structural pressures', 'institutional constraints'])} that {random.choice(['reward this behavior', 'encourage these outcomes', 'make this inevitable'])}.\""
    
    def _generate_outlook_paragraph(self, category: str) -> str:
        """Generate a paragraph about future outlook."""
        return f"Looking ahead, experts predict that this development will likely {random.choice(['set a new precedent', 'trigger similar actions', 'create ripple effects'])} across the {category} landscape. {random.choice(['Industry watchers', 'Policy analysts', 'Technology observers'])} suggest that we may see {random.choice(['increased adoption', 'growing momentum', 'accelerated implementation'])} of similar approaches in the coming months, particularly if {random.choice(['early results prove positive', 'market conditions remain favorable', 'stakeholder support continues'])}."
    
    def _generate_history_paragraph(self, category: str) -> str:
        """Generate a paragraph with historical context."""
        return f"This isn't the first time the {category} sector has {random.choice(['grappled with this issue', 'faced similar challenges', 'encountered this dilemma'])}. Historical parallels can be drawn to {random.choice(['the 2008 financial crisis', 'the dot-com bubble', 'previous regulatory cycles'])}, when similar {random.choice(['decisions were made', 'actions were taken', 'policies were implemented'])} with {random.choice(['mixed results', 'unintended consequences', 'lasting impact'])}."
    
    def _generate_expert(self, category: str) -> str:
        """Generate a fictional expert name."""
        first_names = ['Dr.', 'Professor', 'Dr.', 'Mr.', 'Ms.']
        last_names = ['Thompson', 'Rodriguez', 'Chen', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller']
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_quote(self, category: str, index: int) -> str:
        """Generate a fictional expert quote."""
        quotes = {
            'politics': [
                "The irony here is so perfect it would be beautiful if it weren't governing people's lives.",
                "What we're witnessing is democracy in action, just not the way they taught us in civics class.",
                "The contradiction is so stark it almost seems intentional."
            ],
            'business': [
                "This represents the logical conclusion of shareholder capitalism.",
                "The efficiency gains are remarkable, assuming you ignore the human costs.",
                "What we're seeing is innovation in the service of elimination."
            ],
            'technology': [
                "The technology works perfectly, it's the humanity that needs debugging.",
                "We've successfully automated the problem while eliminating the solution.",
                "The irony is lost on no one except those building it."
            ]
        }
        
        category_quotes = quotes.get(category, [
            "This development reveals fundamental truths about our systems.",
            "The pattern is so consistent it's practically a law of nature.",
            "What we're seeing is the inevitable outcome of current incentives."
        ])
        
        return random.choice(category_quotes)
    
    def _generate_affiliation(self, category: str) -> str:
        """Generate an expert affiliation."""
        affiliations = {
            'politics': ['Georgetown University', 'Brookings Institution', 'Heritage Foundation', 'Center for American Progress'],
            'business': ['Harvard Business School', 'McKinsey & Company', 'Stanford Graduate School of Business', 'MIT Sloan'],
            'technology': ['MIT Media Lab', 'Stanford AI Lab', 'Oxford Internet Institute', 'Berkeley Center for Long-Term Cybersecurity']
        }
        
        return random.choice(affiliations.get(category, ['Independent Research Institute', 'University Think Tank', 'Policy Research Center']))
    
    def _generate_byline(self) -> str:
        """Generate article byline."""
        bylines = ['Staff Writer', 'Political Correspondent', 'Business Reporter', 'Technology Editor']
        return random.choice(bylines)
    
    def _generate_timestamp(self) -> str:
        """Generate article timestamp."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _load_satire_patterns(self) -> Dict:
        """Load satirical patterns and templates."""
        return {
            'contradiction': [
                'discovers that X requires not-X',
                'announces Y while doing opposite of Y',
                'claims to support Z while undermining Z'
            ],
            'corporate_speak': [
                'synergistic optimization',
                'paradigm-shifting innovation',
                'operational excellence through elimination'
            ],
            'political_doublespeak': [
                'fiscal responsibility for others',
                'bipartisan agreement with ourselves',
                'national security through surveillance'
            ]
        }
    
    def _generate_expert_names(self) -> List[str]:
        """Generate a list of plausible expert names."""
        return [
            'Dr. Sarah Mitchell', 'Professor James Chen', 'Dr. Maria Rodriguez',
            'Dr. Robert Thompson', 'Professor Lisa Wang', 'Dr. Michael Johnson',
            'Dr. Emily Davis', 'Professor David Kim', 'Dr. Jennifer Martinez'
        ]
    
    def _load_corporate_speak(self) -> List[str]:
        """Load corporate buzzwords and phrases."""
        return [
            'synergy', 'paradigm shift', 'leverage', 'optimize', 'streamline',
            'rightsizing', 'restructuring', 'operational efficiency', 'shareholder value',
            'core competency', 'strategic alignment', 'operational excellence'
        ]
    
    def _load_political_speak(self) -> List[str]:
        """Load political doublespeak phrases."""
        return [
            'fiscal responsibility', 'government waste', 'taxpayer money',
            'national security', 'public interest', 'bipartisan support',
            'common sense solutions', 'fiscal discipline', 'budgetary constraints'
        ]
    
    def _get_expertise(self, category: str) -> str:
        """Get expertise title for an expert."""
        expertise = {
            'politics': 'political scientist',
            'business': 'economist', 
            'technology': 'technology ethicist'
        }
        return expertise.get(category, 'analyst')
