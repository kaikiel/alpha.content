# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s alpha.content -t test_cover.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src alpha.content.testing.ALPHA_CONTENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/alpha/content/tests/robot/test_cover.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Cover
  Given a logged-in site administrator
    and an add Cover form
   When I type 'My Cover' into the title field
    and I submit the form
   Then a Cover with the title 'My Cover' has been created

Scenario: As a site administrator I can view a Cover
  Given a logged-in site administrator
    and a Cover 'My Cover'
   When I go to the Cover view
   Then I can see the Cover title 'My Cover'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Cover form
  Go To  ${PLONE_URL}/++add++Cover

a Cover 'My Cover'
  Create content  type=Cover  id=my-cover  title=My Cover

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Cover view
  Go To  ${PLONE_URL}/my-cover
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Cover with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Cover title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
