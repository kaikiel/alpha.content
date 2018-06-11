# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s alpha.content -t test_productimg.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src alpha.content.testing.ALPHA_CONTENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/alpha/content/tests/robot/test_productimg.robot
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

Scenario: As a site administrator I can add a ProductImg
  Given a logged-in site administrator
    and an add Product form
   When I type 'My ProductImg' into the title field
    and I submit the form
   Then a ProductImg with the title 'My ProductImg' has been created

Scenario: As a site administrator I can view a ProductImg
  Given a logged-in site administrator
    and a ProductImg 'My ProductImg'
   When I go to the ProductImg view
   Then I can see the ProductImg title 'My ProductImg'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Product form
  Go To  ${PLONE_URL}/++add++Product

a ProductImg 'My ProductImg'
  Create content  type=Product  id=my-productimg  title=My ProductImg

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the ProductImg view
  Go To  ${PLONE_URL}/my-productimg
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a ProductImg with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the ProductImg title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
