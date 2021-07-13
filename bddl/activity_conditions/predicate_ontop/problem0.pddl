(define (problem preserving_food_0)
    (:domain igibson)

    (:objects 
        notebook.n.01_1 - notebook.n.01
        table.n.02_1 - table.n.02
        floor.n.01_1 - floor.n.01
        agent.n.01_1 - agent.n.01
    )

    (:init 
        (ontop notebook.n.01_1 table.n.02_1)
        (inroom table.n.02_1 living_room) 
        (inroom floor.n.01_1 living_room) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )

    (:goal 
        (and 
            (not
                (ontop notebook.n.01_1 table.n.02_1)
            )
        )
    )
)