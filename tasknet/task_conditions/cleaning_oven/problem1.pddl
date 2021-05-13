(define (problem cleaning_oven_1)
    (:domain igibson)

    (:objects
     	crumb.n.03_1 crumb.n.03_2 crumb.n.03_3 - crumb.n.03
    	oven.n.01_1 - oven.n.01
    	ashcan.n.01_1 - ashcan.n.01
    	floor.n.01_1 - floor.n.01
    	dishtowel.n.01_1 - dishtowel.n.01
    	countertop.n.01_1 - countertop.n.01
    	cabinet.n.01_1 - cabinet.n.01
    	agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (inside crumb.n.03_1 oven.n.01_1) 
        (inside crumb.n.03_2 oven.n.01_1) 
        (inside crumb.n.03_3 oven.n.01_1) 
        (dusty oven.n.01_1) 
        (stained oven.n.01_1) 
        (onfloor ashcan.n.01_1 floor.n.01_1) 
        (ontop dishtowel.n.01_1 countertop.n.01_1) 
        (inroom countertop.n.01_1 kitchen) 
        (inroom oven.n.01_1 kitchen) 
        (inroom cabinet.n.01_1 kitchen) 
        (inroom floor.n.01_1 kitchen) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (forall 
                (?crumb.n.03 - crumb.n.03) 
                (inside ?crumb.n.03 ?ashcan.n.01_1)
            ) 
            (not 
                (dusty ?oven.n.01_1)
            ) 
            (not 
                (stained ?oven.n.01_1)
            )
        )
    )
)