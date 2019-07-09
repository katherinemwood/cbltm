from psychopy import core, event, visual, gui, data
from random import randint, choice, shuffle
import os, csv, time

def write_data(filename, fieldnames, data):
    """
    Write a list-of-lists to a csv file.

    :param filename: String. The filename for the csv, including the extension.
    :param fieldnames: List. The column names for the file.
    :param data: A list of lists, in which each element is one row of the csv file.
    :return: None.
    """
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        writer.writeheader()
        for datum in data:
            writer.writerow(dict([(fieldnames[i], datum[i]) for i in range(0, len(fieldnames))]))
    print('Data saved to ' + os.getcwd())


def display_instructions(window, message):
    """
    Display text instructions until a key is pressed.

    :param window: The Psychopy window to draw text to.
    :param message: String. The text to be displayed.
    :return: None.
    """
    instructions = visual.TextStim(window, text=message, color='black', font='Helvetica', units='deg', height=.75)
    instructions.draw(window)
    window.flip()
    key_pressed = False
    while not key_pressed:
        key_pressed = event.waitKeys()
    window.flip()

def draw_fixation(duration, window):
    """
    Draw a fixation cross for a given amount of time, then clear the window.

    :param duration: The amount of time to display the fixation cross, in seconds.
    :param window: The Psychopy window to draw the cross to.
    :return: None.
    """
    vert_arm = visual.Line(window, start=[0, .04], end=[0, -.04], lineWidth=2, lineColor='gray')
    horiz_arm = visual.Line(window, start=[-.025, 0], end=[.025, 0], lineWidth=2, lineColor='gray')
    horiz_arm.draw()
    vert_arm.draw()
    window.flip()
    core.wait(duration)
    window.flip()

def get_response(window, mode, mouse, shapes={}):
    """
    Wait for and collect keyboard or mouse responses.

    :param window: The active Psychopy window.
    :param mode: 'keyboard' if the response is a keypress or 'mouse' if a click.
    :param mouse: The mouse object to monitor.
    :param shapes: A dictionary of Psychopy.visual shapes to monitor for a click.
    :return: The keycode of the key pressed or the index of the shape clicked on.
    """
    if mode == 'keyboard':
        response = ''
        while not response:
            response = event.getKeys(keyList=['left', 'right'])
    elif mode == 'mouse':
        #get mouse input
        mouse.setVisible(1)
        mouse.clickReset()
        mouse.setPos((0, 0))
        response = ''
        while not response:
            for shape in shapes.keys():
                if mouse.isPressedIn(shape):
                   response = shapes[shape]
    mouse.setVisible(0)
    return response

def object_study_task(window, studied_ims, duration, ISI, fillers=[], include_repeats=False):
    """
    Run the object-study portion of the experiment.

    :param window: The Psychopy window to draw to.
    :param studied_ims: The list of filepaths for the images to be studied.
    :param duration: How long each item is presented for, in seconds.
    :param ISI: How long to blank the screen between each item, in seconds.
    :param fillers: The list of filepaths for filler objects from which to draw repeats.
    :param include_repeats: Whether or not to insert duplicate items into the stream.
    :return: A list of lists of subjects' responses to repeated items, or none if not in repeat mode.
    """
    if include_repeats:
        study_instructions = "In this first task, you will be presented with a series of objects. Please observe the objects closely," \
        "as you will be given a memory test later in the session.\n\nRarely, you may notice objects repeating as you study. If you spot a repeated " \
        "object, press the space bar. The object will turn green if you correctly identified a repeat.\n\nIf you have any questions, the " \
        "experimenter will be happy to answer them. If you are ready to begin, press any key."
    else:
        study_instructions = "In this first task, you will be presented with a series of objects. Please observe the objects closely, " \
        "as you will be given a memory test later in the session.\n\nIf you have any questions, the " \
        "experimenter will be happy to answer them. If you are ready to begin, press any key."
    display_instructions(window, study_instructions)
    studied_stream = list(studied_ims)
    if include_repeats:
        # Randomly pick how many and which objects to repeat and insert randomly into the image stream
        repeat_responses = []
        repeats = 6
        repeated_ims = []
        for i in range(0, repeats):
            im = fillers[randint(0, len(fillers) - 1)]
            fillers.remove(im)
            repeated_ims.append([im] * 2)
        hit = visual.Rect(window, width=.2*window.size[1], height=.2*window.size[1], lineColor='green', fillColor='green', opacity=.4, units='pix')
        # insert repeated ims into study stream
        dists0 = [10, 30, 60]
        dists1 = [10, 30, 60]
        for i in range(0, len(repeated_ims)):
            if i < len(repeated_ims) / 2:
               start = randint(0, len(studied_stream) / 2 - 60)
               dist = choice(dists0)
               dists0.remove(dist)
            else:
               start = randint(len(studied_stream) / 2, len(studied_stream) - 60)
               dist = choice(dists1)
               dists1.remove(dist)
            studied_stream.insert(start, repeated_ims[i][0])
            studied_stream.insert(start + dist, repeated_ims[i][1])
    im_clock = core.Clock()
    for i in range(0, len(studied_stream)):
        permaflag = False
        draw_fixation(ISI, window)
        im_present = visual.ImageStim(window, image=studied_stream[i], units='deg')
        im_present.setAutoDraw(True)
        im_clock.reset()
        while im_clock.getTime() < duration:
            im_present.draw()
            window.flip()
            if include_repeats:
                flagged_repeat = event.getKeys(['space'])
                if flagged_repeat and (studied_stream.count(studied_stream[i]) > 1) and (
                    i > studied_stream.index(studied_stream[i])):
                    permaflag = True
                    hit.setAutoDraw(True)
                    hit.draw()
                    window.flip()
                    repeat_responses.append(('hit', i, studied_stream.index(studied_stream[i])))
                elif flagged_repeat:
                    repeat_responses.append(('f_a', i, studied_stream.index(studied_stream[i])))  # false alarm
        if include_repeats:
            hit.setAutoDraw(False)
            if (not permaflag) and (studied_stream.count(studied_stream[i]) > 1) and (i > studied_stream.index(studied_stream[i])):
                repeat_responses.append(('miss', i, studied_stream.index(studied_stream[i])))
        im_present.setAutoDraw(False)
        window.flip()
        if ((i + 1) == len(studied_stream) // 2):
            break_message = "You are halfway through the study task. Take a brief break. Press any key to resume."
            display_instructions(window, break_message)
    return repeat_responses if include_repeats else None

def object_memory_task(window, mouse, studied_ims, studied_complement, trials, ISI):
    """
    Present the 2AFC memory test task. Takes in lists of studied and filler items.
    Category selection of images is random on each trial, but the test and foil objects will always come from the
    same category.
    :param window: The Psychopy window on which to present the task.
    :param mouse: The mouse object in use.
    :param studied_ims: The list of filenames of the studied images.
    :param studied_complement: The list of exemplars corresponding to each study item.
    :param trials: The number of trials of the task to run.
    :param ISI: How long to wait between each trial.
    :return: A list of lists of subjects' responses, whether it was correct, and which items were shown
            on each trial.
    """
    memory_instructions = "In this task, you will be presented with pairs of images. You will have seen one of them before during the study " \
    "portion of this experiment. If it is the image on the left, use the left arrow key to respond. If it is on the right, " \
    "use the right arrow key. If you are not sure or cannot remember, respond with your best guess. If you have any " \
    "questions, the experimenter will be happy to answer them. If you are ready to begin, press any key."
    display_instructions(window, memory_instructions)
    coords = [(-1*window.size[0]/4, 0), (window.size[0]/4, 0)]
    object_responses = []
    for i in range(0, trials):
        trial_data = []
        trial_data.append('memory')
        trial_idx = randint(0, len(studied_ims) - 1)
        test_item = studied_ims[trial_idx]
        studied_ims.remove(test_item)
        foil_item = studied_complement[trial_idx]
        studied_complement.remove(foil_item)
        #present image and foil; hold until response is received
        test_side = choice([0, 1])
        test_image = visual.ImageStim(window, image=test_item, units='pix', pos=coords[test_side])
        foil_image = visual.ImageStim(window, image=foil_item, units = 'pix', pos=coords[not test_side])
        test_image.draw()
        foil_image.draw()
        window.flip()
        resp = get_response(window, mode='keyboard', mouse=mouse)
        window.flip()
        core.wait(ISI)
        #add to response record
        if (resp == ['left'] and test_side == 0) or (resp == ['right'] and test_side == 1):
            response = 1
        else:
            response = 0
        trial_data.append(response)
        trial_data.append(resp[0])
        trial_data.append(test_item)
        trial_data.append(foil_item)
        trial_data.append(core.getTime())
        trial_data.append([foil_item, test_item][response])
        trial_data = trial_data + [0, 0, 0, 0, 0] #add the null fillers
        object_responses.append(trial_data)
    return object_responses

def cd_task(mode, window, mouse, slots, slot_size, targets, prechange, fillers, items_per_array, trials, prechange_dur, ISI):
    """
    Present the 6AFC memory task or a change detection task.

    :param mode: A string indicating what kind of trial to run. All modes but "unstudied" use a familiar object in
                the post-change array, but vary in their instructions. "unstudied" mode uses only unfamiliar objects.
                "flipped" mode collects an additional response each trial.
    :param window: The Psychopy window on which to present the task.
    :param mouse: The mouse object to monitor for clicks.
    :param slots: The positions of each image, as a list of (x, y) tuples.
    :param slot_size: The size of each slot, and therefore the size of each image.
    :param targets: A list of filenames for each of the post-change objects.
    :param prechange: A list of filenames for each of the pre-change objects.
    :param fillers: A list of filenames of filler objects that do not change on each trial.
    :param items_per_array: The number of items to present on each trial.
    :param trials: The number of trials to run.
    :param prechange_dur: How long the prechange array remains visible, in seconds
    :param ISI: The blank between the pre-change and post-change array, in seconds.
    :return: A list of lists containing the subjects' responses and details about the display.
    """
    if mode == '6afc':
        instructions = "In this task, you will be presented with a series of arrays of six images. You will have seen one of them before " \
        "during the study portion of this experiment. Click on the image you have seen before, or your best guess if you cannot " \
        "remember or are not sure. \n\nIf you have any questions, the experimenter will be happy to answer them. If you are " \
        "ready to begin, press any key."
    elif mode == 'unstudied' or mode == 'studied':
        instructions = "In this task, you will be presented with an array of six objects. This array will be visible for " \
        "a few seconds, then it will disappear and be replaced by a second array of six objects. \n\nYour " \
        "task is to click on the object in the second array that changed from the first array. If you are not sure or don't " \
        "think anything changed, respond with your best guess.\n\nIf you have any questions, the experimenter will be happy to " \
        "answer them. If you are ready to begin, press any key."
    elif mode == 'hybrid':
        instructions = "In this task, just as before, you will be presented with an array of six objects, followed by "\
        "a second array of six objects. This time, if a familiar object (that is, an object that you saw when you were studying objects " \
        "at the beginning of the experiment) appears in the second array, it will be the one that changed from the first " \
        "array. Your task is to click on the changed object.\n\nIf you have any questions, the experimenter will be happy to answer them. " \
        "If you are ready to begin, press any key."
    elif mode == 'ignore_first':
        instructions = "In this task, just as before, you will be presented with an array of six objects, followed by " \
        "a second array of six objects. If a familiar object appears in the second array, it will be the one that changed from the first " \
        "array. Your task is to click on the changed object.\n\nIf you have any questions, the experimenter will be happy to answer them. " \
        "If you are ready to begin, press any key."
    elif mode == 'strategy':
        instructions = "In this task, just as before, you will be presented with an array of six objects, followed by " \
        "a second array of six objects. This time, use the following strategy: \n\n" \
        "1. Try to find what changed from the first array. \n\n" \
        "2. If you can't tell what changed, look for a familiar item. \n\n" \
        "3. If you find a familiar item, select that as your answer. \n\n" \
        "If you have any questions, the experimenter will be happy to answer them. If you are ready to begin, press any key."
    elif mode == 'flipped':
        instructions = "In this task, you will be looking for an object you saw during the study phase. We will present you with " \
        "two arrays. The first array will flash, and then it will be followed by a second array. \n\nLook for the familiar object in the second array. " \
        "\n\nIf you have difficulty remembering, see if you can tell which object is different from the first array. If an object changes from the " \
        "first array, it will always change into a familiar object, so this can help you identify it.\n\nIf you have any questions, the experimenter "\
        "will be happy to answer them. Press any key to begin."
    display_instructions(window, instructions)
    cd_data = []
    for i in range(0, trials):
        trial_data = []
        trial_data.append(mode)
        test_slot = randint(1, items_per_array)
        trial_idx = randint(0, len(targets) - 1)
        test_im = targets[trial_idx]
        targets.remove(test_im)
        bait_im = prechange[trial_idx]
        prechange.remove(bait_im)
        filler_ims = []
        for slot in range(1, items_per_array + 1):
            filler_im = choice(fillers)
            filler_ims.append(filler_im)
            fillers.remove(filler_im)
        # create a dictionary with the slot number mapped to the image it will contain; does not include
        # the test image, which will be overwritten in the full-CD mode branch
        # here, convert image index to ImageStim by indexing out of the 'images' argument
        # Because ImageStim objects do not have an "isPressedIn" method, draw invisible Rect objects
        # over the top. Monitor these for a click instead.
        image_pos = {}
        ghosts = {}
        for i in range(1, items_per_array + 1):
            ghosts[
                visual.Rect(window, pos=slots[i - 1], units='pix', width=slot_size, height=slot_size,
                            opacity=0.0)] = i
            if i == test_slot:
                if mode != '6afc':
                    image_pos[i] = visual.ImageStim(window, image=bait_im, size=slot_size, units='pix',
                                                    pos=slots[i - 1])
                else:
                    image_pos[i] = visual.ImageStim(window, image=test_im, size=slot_size, units='pix',
                                                    pos=slots[i - 1])
            else:
                image_pos[i] = visual.ImageStim(window, image=filler_ims[i - 1], size=slot_size, units='pix',
                                                pos=slots[i - 1])
        # initialize the visual.ImageStims and transparent "ghost shapes",
        # draw them to the screen, then collect response
        if mode != '6afc':
            for i in image_pos.keys():
                img = image_pos[i]
                img.draw(window)
            window.flip()
            core.wait(prechange_dur)
            window.flip()
            core.wait(ISI)
            image_pos[test_slot] = visual.ImageStim(window, image=test_im, size=slot_size, units='pix', pos=slots[test_slot - 1])
        for i in image_pos.keys():
            img = image_pos[i]
            img.draw(window)
            list(ghosts.keys())[i - 1].draw(window)
        window.flip()
        response = get_response(window, 'mouse', mouse, ghosts)
        window.flip()
        if response == test_slot:
            correct = 1
        else:
            correct = 0
        if mode == 'flipped':
            strat_inst = "Did the object you picked change from the first array? Please use the arrow keys to respond, " \
            "left for 'no' and right for 'yes'."
            instructions = visual.TextStim(window, text=strat_inst)
            instructions.draw(window)
            window.flip()
            lr_input = get_response(window, 'keyboard', mouse=mouse)
            if lr_input==['right']:
                if correct:
                   lr_response = 'hit' #picked right object and noticed change
                elif not correct:
                   lr_response='f_a' #picked wrong object, declared change
            elif lr_input==['left']:
                if correct:
                   lr_response = 'f_n' #picked right object, said no change
                elif not correct:
                   lr_response = 'miss' #wrong object, no change
            else:
                lr_correct = 0
        trial_data.append(correct)
        trial_data.append(response)
        trial_data.append(test_im)
        trial_data.append(bait_im)
        if mode == 'flipped':
            trial_data.append(lr_response)
        else:
            trial_data.append(core.getTime())
        trial_data.append(image_pos[response].image)
        [trial_data.append(filler) for filler in filler_ims]
        cd_data.append(trial_data)
    return cd_data

def getQualData(window):
    """
    Run the qualitative data task. Subjects are presented with a screen on which to type.
    :param window: The Psychopy window on which to show the text.
    :return: The string that subjects' typed.
    """
    qinst = "Please describe your approach to the task you just completed. Did you find it easier or harder than "\
    "the first task you completed? Were you able to use the provided strategy? Did the strategy help, or did you find it hard to "\
    "use or unituitive? Please respond with a few sentences. When you have finished entering your response, please press the enter key." \
    "Press any key to advance to the next screen and begin typing."
    display_instructions(window, qinst)
    strat=''
    echo = visual.TextStim(window, text=strat,color="black", units='deg', height = .5, wrapWidth = 12)
    echo.setAutoDraw(True)
    #until return pressed, listen for letter keys & add to text string
    cap_next = True
    punctuation = {'period': '.', 'space': ' ', 'apostrophe':"'", 'question': '?', 'exclamation': '!',
                   'comma': ',', 'colon':':', 'semicolon':';', 'parenleft': '(', 'parenright':')'}
    while event.getKeys(keyList=['return'])==[] or len(strat) == 0:
        letterlist=event.getKeys()
        for l in letterlist:
            if l == 'lshift':
                cap_next = True
            elif l =='backspace' and len(strat) > 0:
                strat=strat[:-1]
            elif l in punctuation.keys():
                strat += punctuation[l]
            elif l != 'backspace' and not len(l) > 1:
                if cap_next:
                   strat += l.capitalize()
                   cap_next = False
                else:
                   strat += l
        #continually redraw text onscreen until return pressed
        echo.setText(strat)
        window.flip()
    echo.setAutoDraw(False)
    event.clearEvents()
    return strat

def run_experiment(experiment, win):
    """
    Run a particular experiment from beginning to end and save the data.

    :param experiment: The integer of the experiment to run.
    :param win: The Psychopy window to use.
    :return: None.
    """
    # import images
    exemplar0 = 'Stimuli/exemplarA/'
    exemplar1 = 'Stimuli/exemplarB/'
    fillers = 'Stimuli/OBJECTSALL/'

    images = {'exemplarset0': [exemplar0 + im for im in sorted(os.listdir(exemplar0))[1:]],
              'exemplarset1': [exemplar1 + im for im in sorted(os.listdir(exemplar1))[1:]],
              'fillers': [fillers + im for im in sorted(os.listdir(fillers))[1:]]}

    # subject info
    exp_info = {'SubjID': ''}
    ex_info_dlg = gui.DlgFromDict(dictionary=exp_info, title='Experiment Log')
    # output file
    file_name = exp_info['SubjID'] + '_' + time.strftime("%c") + '_CBLTM_'+ str(experiment) + '.csv'

    # Initialize mouse
    mouse = event.Mouse(win)
    mouse.setVisible(0)

    # image categories and order
    trials_per_task = 1

    # study task parameters
    study_dur = 3
    ISI_study = .5

    # change detection task parameters
    items_per_array = 6
    prechange_dur = 5 if experiment > 4 else 1.2
    ISI_cd = .4
    imsize = .2*win.size[1] / 2
    # carve up the window into a grid with the approprite number of slots
    # used to draw items and to draw the transparent shapes that will be used for mouse input
    diameter = .8*win.size[1] / 2
    radius = diameter / 2
    slot_size = imsize  # this is the size of the images used; slot will be precisely as large
    # These coordinates represent the center of the "slot" to which the images will be drawn. The slots are numbered
    # clockwise, starting at 12 o'clock.
    # This utilizes hexagon geometry to calculate the center of the 6 slots.
    slots = [(0, radius), (3 ** .5 * radius / 2, radius / 2), (3 ** .5 * radius / 2, -radius / 2),
             (0, -radius), (-(3 ** .5 * radius / 2), -radius / 2), (-(3 ** .5 * radius / 2), radius / 2)]

    #How many tasks requiring studied and unstudied images, respectively, there are in each
    #experiment.
    task_blocks = {1: (3, 1), 2: (4, 0), 3: (2, 1), 4: (3, 1), 5: (2, 1), 6: (2, 1)}[experiment]

    # Select studied and unstudied images. Both need to come from the exemplar sets.
    # Studied images will be used in the memory and change blindness tasks, and
    # unstudied images will be used in the baseline change blindness task.

    allexemplars = list(range(0, len(images['exemplarset0'])))
    shuffle(allexemplars)

    studied = []
    studied_complement = []
    unstudied = []
    unstudied_complement = []
    exemplar_choices = ['exemplarset0', 'exemplarset1']
    for i in range(0, task_blocks[0] * trials_per_task):
        exemplar_id = allexemplars[i]
        first_member = choice([0, 1])
        exemplar_pair = exemplar_choices[first_member]
        studied.append(images[exemplar_pair][exemplar_id])
        studied_complement.append(images[exemplar_choices[not first_member]][exemplar_id])

    for i in range(task_blocks[0] * trials_per_task, (task_blocks[0] + task_blocks[1]) * trials_per_task):
        exemplar_id = allexemplars[i]
        first_member = choice([0, 1])
        exemplar_pair = exemplar_choices[first_member]
        unstudied.append(images[exemplar_pair][exemplar_id])
        unstudied_complement.append(images[exemplar_choices[not first_member]][exemplar_id])

    exp_instructions = "Before the experiment begins, please take a moment to silence your cell phone." \
    "\nThis experiment will make use of the chinrest in front of you to make sure you are a fixed distance from the monitor, " \
    "so take a moment to adjust it to a comfortable height. If it is too tall or too short, please let the experimenter know." \
    "\n\nThe experiment will take approximately 40 minutes to complete with opportunities for breaks. Thank you for your participation and attention." \
    "\n\nWhen the experimenter clears you to start, press any key."

    completed_instructions = "Thank you for your participation. Please see experimenter for your debriefing. Press any key to exit."
    display_instructions(win, exp_instructions)

    if experiment == 1:
        field_names = ['trial_type', 'correct', 'raw_response', 'test_image', 'bait_image', 'timestamp', 'response_image',
                      'filler1', 'filler2', 'filler3', 'filler4', 'filler5']
        object_study_task(win, studied, study_dur, ISI_study)
        studied_CD_data = cd_task('studied', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                                  items_per_array, trials_per_task, prechange_dur, ISI_cd)
        unstudied_CD_data = cd_task('unstudied', win, mouse, slots, slot_size, unstudied, unstudied_complement,
                                    images['fillers'], items_per_array, trials_per_task, prechange_dur, ISI_cd)
        afc6_data = cd_task('6afc', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                                 items_per_array, trials_per_task, prechange_dur, ISI_cd)
        memory_data = object_memory_task(win, mouse, studied, studied_complement, trials_per_task, ISI_cd)

        experiment_data = studied_CD_data + unstudied_CD_data + afc6_data + memory_data
    elif experiment == 2:
        field_names = ['trial_type', 'correct', 'raw_response', 'test_image', 'bait_image', 'timestamp', 'response_image',
            'filler1', 'filler2', 'filler3', 'filler4', 'filler5']
        object_study_task(win, studied, study_dur, ISI_study)
        studied_CD_data = cd_task('studied', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                                  items_per_array, trials_per_task, prechange_dur, ISI_cd)
        ignore_CD_data = cd_task('ignore_first', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                                 items_per_array, trials_per_task, prechange_dur, ISI_cd)
        afc6_data = cd_task('6afc', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                                 items_per_array, trials_per_task, prechange_dur, ISI_cd)
        memory_data = object_memory_task(win, mouse, studied, studied_complement, trials_per_task, ISI_cd)

        experiment_data = studied_CD_data + ignore_CD_data + afc6_data + memory_data
    elif experiment == 3:
        field_names = ['trial_type', 'correct', 'raw_response', 'test_image', 'bait_image', 'timestamp',
                      'response_image', 'filler1', 'filler2', 'filler3', 'filler4', 'filler5']

        object_study_task(win, studied, study_dur, ISI_study)
        unstudied_CD_data = cd_task('unstudied', win, mouse, slots, slot_size, unstudied, unstudied_complement,
                                    images['fillers'], items_per_array, trials_per_task, prechange_dur, ISI_cd)
        strategy_CD_data = cd_task('strategy', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                                   items_per_array, trials_per_task, prechange_dur, ISI_cd)
        strat_data = getQualData(win)
        afc6_data = cd_task('6afc', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                                 items_per_array, trials_per_task, prechange_dur, ISI_cd)

        experiment_data = unstudied_CD_data + strategy_CD_data + afc6_data
        stratfile = open(exp_info['SubjID'] + '_strat_data_ex3_' + time.strftime("%c") + '.txt', 'w')
        stratfile.write(strat_data)
        stratfile.close()
    elif experiment == 4:
        field_names = ['trial_type', 'correct', 'raw_response', 'test_image', 'bait_image', 'lr_response',
                      'response_image', 'filler1', 'filler2', 'filler3', 'filler4', 'filler5']
        # output file nback
        nback_file_name = exp_info['SubjID'] + '_' + time.strftime("%c") + '_nback.csv'
        nback_field_names = ['response', 'index', 'first_occurence']

        nback_responses = object_study_task(win, studied, study_dur, ISI_study, images['fillers'], include_repeats = True)
        flipped_CD_data = cd_task('flipped', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        unstudied_CD_data = cd_task('unstudied', win, mouse, slots, slot_size, unstudied, unstudied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        memory_6AFC_data = cd_task('6afc', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        memory_2AFC = object_memory_task(win, mouse, studied, studied_complement, trials_per_task, ISI_cd)
        experiment_data = flipped_CD_data + unstudied_CD_data + memory_6AFC_data + memory_2AFC
        write_data(nback_file_name, nback_field_names, nback_responses)
    elif experiment == 5:
        field_names = ['trial_type', 'correct', 'raw_response', 'test_image', 'bait_image', 'timestamp', 'response_image',
                       'filler1', 'filler2', 'filler3', 'filler4', 'filler5']

        object_study_task(win, studied, study_dur, ISI_study)
        unstudied_CD_data = cd_task('unstudied', win, mouse, slots, slot_size, unstudied, unstudied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        afc6_data = cd_task('6afc', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        hybrid_CD_data = cd_task('hybrid', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        experiment_data = unstudied_CD_data + hybrid_CD_data + afc6_data
    elif experiment == 6:
        field_names = ['trial_type', 'correct', 'raw_response', 'test_image', 'bait_image', 'timestamp', 'response_image',
            'filler1', 'filler2', 'filler3', 'filler4', 'filler5']
        object_study_task(win, studied, study_dur, ISI_study)
        unstudied_CD_data = cd_task('unstudied', win, mouse, slots, slot_size, unstudied, unstudied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        hybrid_CD_data = cd_task('hybrid', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)
        afc6_data = cd_task('6afc', win, mouse, slots, slot_size, studied, studied_complement, images['fillers'],
                    items_per_array, trials_per_task, prechange_dur, ISI_cd)

        experiment_data = unstudied_CD_data + hybrid_CD_data + afc6_data

    write_data(file_name, field_names, experiment_data)

    display_instructions(win, completed_instructions)
    win.close()

run_experiment(1, win = visual.Window([1080, 720], allowGUI=True, monitor='testMonitor', color='white', units='pix'))