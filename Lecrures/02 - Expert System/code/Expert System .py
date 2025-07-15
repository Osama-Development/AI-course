class Fact:
    def __init__(self, description):
        self.description = str(description)
    def __repr__(self):
        return f'Fact("{self.description}")'
    def __eq__(self, other):
        return isinstance(other, Fact) and self.description == other.description
    def __hash__(self):
        return hash(self.description)

class Rule:
    def __init__(self, conditions, conclusion):
        self.conditions = conditions
        self.conclusion = conclusion
    def __repr__(self):
        return f"Rule(IF {' AND '.join(map(repr, self.conditions))} THEN {repr(self.conclusion)})"


class SimpleExpertSystem:
    def __init__(self):
        self.rules = []
        self.facts = set()

    def add_fact(self, fact):
        self.facts.add(fact)

    def add_rule(self, rule):
        self.rules.append(rule)
        
    def get_initial_facts(self):
        print("="*20 + "\nمرحباً بك في نظام تشخيص مشاكل الإنترنت.\n" + "="*20)
        print("أجب على الأسئلة التالية بـ 'نعم' أو 'لا'.")

        # طرح أسئلة محددة بدلاً من الإدخال المفتوح
        if input("هل الإنترنت لا يعمل؟ (نعم/لا) > ").lower() == 'نعم':
            self.add_fact(Fact("الإنترنت_لا_يعمل"))
        else: # إذا كان الإنترنت يعمل، لا داعي لإكمال التشخيص
            print("رائع! يبدو أن كل شيء على ما يرام.")
            return False # إشارة للتوقف

        if Fact("الإنترنت_لا_يعمل") in self.facts:
            answer = input("ما هي حالة لمبة الإنترنت على الراوتر؟ (خضراء/برتقالية/لا_تعمل) > ").lower()
            if answer == "خضراء":
                self.add_fact(Fact("لمبة_الراوتر_خضراء"))
            elif answer == "برتقالية":
                 self.add_fact(Fact("لمبة_الراوتر_برتقالية"))
            elif answer == "لا_تعمل":
                 self.add_fact(Fact("لمبة_الراوتر_لا_تعمل"))

        print("\nشكراً لك، تم جمع الحقائق الأولية.")
        return True # إشارة للاستمرار

    def run(self):
        print("\n" + "="*20 + "\nبدء تشغيل محرك الاستدلال...\n" + "="*20)
        while True:
            activated_rules = []
            for rule in self.rules:
                if all(c in self.facts for c in rule.conditions) and rule.conclusion not in self.facts:
                    activated_rules.append(rule)
            
            if not activated_rules:
                print("... لا توجد قواعد أخرى يمكن تفعيلها. محرك الاستدلال يتوقف.")
                break
            
            selected_rule = activated_rules[0]
            print(f"  [تفعيل القاعدة]: {repr(selected_rule)}")
            self.facts.add(selected_rule.conclusion)
            print(f"  [حقيقة جديدة مستنتجة]: {selected_rule.conclusion}")

        print("\n" + "="*20 + "\nالاستنتاجات النهائية:\n" + "="*20)
        final_conclusions = [f for f in self.facts if "الحل_هو" in f.description or "المشكلة_هي" in f.description]
        if not final_conclusions:
            print("- لم يتم التوصل إلى حل أو تشخيص نهائي.")
        else:
            for fact in final_conclusions:
                print(f"- {fact.description.replace('_', ' ')}")
        print("="*20)

class InternetTroubleshooter(SimpleExpertSystem):
    def __init__(self):
        super().__init__() # استدعاء دالة البناء للفئة الأم
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        # --- تعريف كل الحقائق الممكنة ---
        f1 = Fact("الإنترنت_لا_يعمل")
        f2 = Fact("لمبة_الراوتر_لا_تعمل")
        f3 = Fact("لمبة_الراوتر_برتقالية")
        f4 = Fact("لمبة_الراوتر_خضراء")
        f5 = Fact("جرب_إعادة_تشغيل_الراوتر")
        f6 = Fact("المشكلة_لا_تزال_موجودة")
        f7 = Fact("حدد_نطاق_المشكلة")
        f8 = Fact("المشكلة_على_جهاز_واحد_فقط")
        f9 = Fact("المشكلة_على_كل_الأجهزة")
        
        c1 = Fact("المشكلة_هي_كهرباء_الراوتر")
        c2 = Fact("المشكلة_هي_إشارة_الشركة")
        c3 = Fact("المشكلة_في_الجهاز_نفسه")
        c4 = Fact("المشكلة_في_الراوتر_أو_الشركة")
        
        s1 = Fact("الحل_هو_فحص_كابل_الكهرباء_والمقبس")
        s2 = Fact("الحل_هو_الاتصال_بشركة_الإنترنت")
        s3 = Fact("الحل_هو_إعادة_تشغيل_الجهاز_وفحص_إعداداته")

        # --- تعريف كل القواعد ---
        self.add_rule(Rule(conditions=[f1, f2], conclusion=c1))
        self.add_rule(Rule(conditions=[f1, f3], conclusion=c2))
        self.add_rule(Rule(conditions=[f1, f4], conclusion=f5))
        self.add_rule(Rule(conditions=[f5, f6], conclusion=f7)) # هذا الجزء يحتاج لتفاعل إضافي
        self.add_rule(Rule(conditions=[f7, f8], conclusion=c3)) # وهذا أيضاً
        self.add_rule(Rule(conditions=[f7, f9], conclusion=c4)) # وهذا أيضاً
        self.add_rule(Rule(conditions=[c1], conclusion=s1))
        self.add_rule(Rule(conditions=[c2], conclusion=s2))
        self.add_rule(Rule(conditions=[c3], conclusion=s3))
        self.add_rule(Rule(conditions=[c4], conclusion=s2)) # إذا كانت المشكلة عامة اتصل بالشركة
        
if __name__ == "__main__":
    # 1. أنشئ نسخة من نظامك الخبير المتخصص
    troubleshooter = InternetTroubleshooter()
    
    # 2. قم بجمع الحقائق الأولية من المستخدم
    should_run = troubleshooter.get_initial_facts()
    
    # 3. إذا كان لدى المستخدم مشكلة فعلاً، قم بتشغيل المحرك
    if should_run:
        troubleshooter.run()